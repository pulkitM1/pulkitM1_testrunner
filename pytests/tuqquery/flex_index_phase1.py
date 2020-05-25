from .tuq import QueryTests
from pytests.fts.random_query_generator.rand_query_gen import DATASET
from collections import Mapping, Sequence, Set, deque
import json

class FlexIndexTests(QueryTests):

    users = {}

    def suite_setUp(self):
        super(FlexIndexTests, self).suite_setUp()

    def setUp(self):
        super(FlexIndexTests, self).setUp()

        self.log.info("==============  FlexIndexTests setuAp has started ==============")
        self.log_config_info()
        self.dataset = self.input.param("flex_dataset", "emp")
        self.use_index_name_in_query = bool(self.input.param("use_index_name_in_query", True))
        self.expected_gsi_index_map = {}
        self.expected_fts_index_map = {}
        self.custom_map = self.input.param("custom_map", False)
        self.bucket_name = self.input.param("bucket_name", 'default')
        self.flex_query_option = self.input.param("flex_query_option", "flex_use_fts_query")
        self.log.info("==============  FlexIndexTests setup has completed ==============")

    def tearDown(self):
        self.log.info("==============  FlexIndexTests tearDown has started ==============")
        self.log_config_info()
        self.log.info("==============  FlexIndexTests tearDown has completed ==============")
        super(FlexIndexTests, self).tearDown()

    def suite_tearDown(self):
        self.log.info("==============  FlexIndexTests suite_tearDown has started ==============")
        self.log_config_info()
        self.log.info("==============  FlexIndexTests suite_tearDown has completed ==============")
        super(FlexIndexTests, self).suite_tearDown()

# ============================ # Utils ===========================================

    def compare_results_with_gsi(self, flex_query, gsi_query):
        try:
            flex_result = self.run_cbq_query(flex_query)["results"]
            self.log.info("Number of results from flex query: {0} is {1}".format(flex_query, len(flex_result)))
        except Exception as e:
            self.log.info("Failed to run flex query: {0}".format(flex_query))
            self.log.error(e)
            return False

        try:
            gsi_result = self.run_cbq_query(gsi_query)["results"]
            self.log.info("Number of results from gsi query: {0} is {1}".format(gsi_query, len(gsi_result)))
        except Exception as e:
            self.log.info("Failed to run gsi query: {0}".format(gsi_query))
            self.log.error(e)
            return False

        if len(flex_result) != len(gsi_result):
            self.log.info("length of results of GSI and Flex query differs")
            return False

        if sorted(flex_result) != sorted(gsi_result):
            self.log.info("Sort of results of GSI and Flex query differs")
            return False

        return True

    def get_gsi_fields_partial_sargability(self):
        fts_fields = self.query_gen.fields
        available_fields = DATASET.CONSOLIDATED_FIELDS
        gsi_fields = []
        for field in available_fields:
            field_found = False
            for k, v in fts_fields.items():
                if field in v:
                    field_found = True
                    break
            if not field_found:
                gsi_fields.append(field)
        return list(set(gsi_fields))

    def create_gsi_indexes(self, gsi_fields):
        count = 0
        self.expected_gsi_index_map = {}
        for field in gsi_fields:
            field = self.query_gen.replace_underscores(field)
            field_proxy = field
            #handling array fields
            if field == "languages_known":
                field = "ALL ARRAY v for v in languages_known END"
            if field == "manages.reports":
                field = "ALL ARRAY v for v in manages.reports END"
            if field_proxy not in self.expected_gsi_index_map.keys() and field_proxy is not "type":
                gsi_index_name = "gsi_index_" + str(count)
                self.run_cbq_query("create index {0} on `{2}`({1})".format(gsi_index_name, field, self.bucket_name))
                self.expected_gsi_index_map[field_proxy] = [gsi_index_name]
                count += 1
        self.log.info("expected_gsi_index_map {0}".format(self.expected_gsi_index_map))

    def get_all_indexnames_from_response(self, response_json):
        queue = deque([response_json])
        index_names = []
        while queue:
            node = queue.popleft()
            nodevalue = node
            if type(node) is tuple:
                nodekey = node[0]
                nodevalue = node[1]

            if isinstance(nodevalue, Mapping):
                for k, v in nodevalue.items():
                    queue.extend([(k, v)])
            elif isinstance(nodevalue, (Sequence, Set)) and not isinstance(nodevalue, basestring):
                queue.extend(nodevalue)
            else:
                if nodekey == u"index" and nodevalue not in index_names:
                    index_names.append(str(nodevalue))
        return index_names

    def check_if_expected_index_exist(self, result, expected_indexes):
        actual_indexes = self.get_all_indexnames_from_response(result)
        found = True
        self.log.info("Actual indexes present: {0}, Expected Indexes: {1}".format(sorted(actual_indexes), sorted(expected_indexes)))
        for index in actual_indexes:
            if index not in expected_indexes:
                found = False
        return found

    def get_expected_indexes(self, flex_query, expected_index_map):
        available_fields = DATASET.CONSOLIDATED_FIELDS
        expected_indexes = []
        for field in available_fields:
            field = self.query_gen.replace_underscores(field)
            if " {0}".format(field) in flex_query and field in expected_index_map.keys():
                for index in expected_index_map[field]:
                    expected_indexes.append(index)

        return list(set(expected_indexes))

    def run_query_and_validate(self, query_list):
        failed_to_run_query = []
        not_found_index_in_response = []
        result_mismatch = []
        iteration = 1

        for query in query_list:
            query_num = iteration
            iteration += 1
            self.log.info("======== Running Query # {0} =======".format(query_num))
            flex_query = query.format("USE INDEX (USING FTS, USING GSI)")
            gsi_query = query.format("")
            explain_query = "explain " + flex_query
            self.log.info("Query : {0}".format(explain_query))
            try:
                result = self.run_cbq_query(explain_query)
            except Exception as e:
                self.log.info("Failed to run query")
                self.log.error(e)
                failed_to_run_query.append(query_num)
                continue
            try:
                self.assertTrue(self.check_if_expected_index_exist(result, ["default_index"]))
            except Exception as e:
                self.log.info("Failed to find fts index name in plan query")
                self.log.error(e)
                not_found_index_in_response.append(query_num)
                continue

            if not self.compare_results_with_gsi(flex_query, gsi_query):
                self.log.error("Result mismatch found")
                result_mismatch.append(query_num)

            self.log.info("======== Done =======")

        return failed_to_run_query, not_found_index_in_response, result_mismatch


    def run_queries_and_validate(self, partial_sargability=None):
        iteration = 1
        failed_to_run_query = []
        not_found_index_in_response = []
        result_mismatch = []
        for flex_query_ph, gsi_query in zip(self.query_gen.fts_flex_queries, self.query_gen.gsi_queries):
            query_num = iteration
            iteration += 1
            self.log.info("======== Running Query # {0} =======".format(query_num))
            expected_fts_index = []
            expected_gsi_index = []
            if self.flex_query_option != "flex_use_gsi_query":
                expected_fts_index = self.get_expected_indexes(flex_query_ph, self.expected_fts_index_map)
            expected_gsi_index = self.get_expected_indexes(flex_query_ph, self.expected_gsi_index_map)
            flex_query = self.get_runnable_flex_query(flex_query_ph, expected_fts_index, expected_gsi_index)
            if self.flex_query_option == "flex_use_gsi_query":
                expected_gsi_index.append("primary_gsi_index")
            flex_query = json.loads(json.dumps(flex_query, ensure_ascii=False)).encode('utf-8')
            gsi_query = json.loads(json.dumps(gsi_query, ensure_ascii=False)).encode('utf-8')
            # issue MB-39493
            if partial_sargability and self.flex_query_option == "flex_use_fts_query" and flex_query.count("OR") > 1:
               expected_gsi_index.append("primary_gsi_index")
            explain_query = "explain " + flex_query
            self.log.info("Query : {0}".format(explain_query))
            try:
                result = self.run_cbq_query(explain_query)
            except Exception as e:
                self.log.info("Failed to run query")
                self.log.error(e)
                failed_to_run_query.append(query_num)
                continue
            try:
                self.assertTrue(self.check_if_expected_index_exist(result, expected_fts_index + expected_gsi_index))
            except Exception as e:
                self.log.info("Failed to find fts index name in plan query")
                self.log.error(e)
                not_found_index_in_response.append(query_num)
                continue

            if not self.compare_results_with_gsi(flex_query, gsi_query):
                self.log.error("Result mismatch found")
                result_mismatch.append(query_num)

            self.log.info("======== Done =======")

        return failed_to_run_query, not_found_index_in_response, result_mismatch

    def merge_smart_fields(self, smart_fields1, smart_fields2):
        combined_fields = {}
        for key in smart_fields1.keys():
            if key in smart_fields2.keys():
                combined_fields[key] = list(set(smart_fields1[key] + smart_fields2[key]))
            else:
                combined_fields[key] = smart_fields1[key]

        for key in smart_fields2.keys():
            if key not in smart_fields1.keys():
                combined_fields[key] = smart_fields2[key]
        return combined_fields

    def get_runnable_flex_query(self, flex_query_ph, expected_fts_index, expected_gsi_index):
        use_fts_hint = "USING FTS"
        use_gsi_hint = "USING GSI"
        final_hint = ""
        if self.flex_query_option == "flex_use_fts_query" or self.flex_query_option == "flex_use_fts_gsi_query":
            if self.use_index_name_in_query:
                for index in expected_fts_index:
                    if final_hint == "":
                        final_hint = "{0} {1}". format(index, use_fts_hint)
                    else:
                        final_hint = "{0}, {1} {2}".format(final_hint, index, use_fts_hint)
            else:
                final_hint = use_fts_hint

        if self.flex_query_option == "flex_use_gsi_query" or self.flex_query_option == "flex_use_fts_gsi_query":
            if self.use_index_name_in_query and expected_gsi_index:
                for index in expected_gsi_index:
                    if final_hint == "":
                        final_hint = "{0} {1}". format(index, use_gsi_hint)
                    else:
                        final_hint = "{0}, {1} {2}".format(final_hint, index, use_gsi_hint)
            elif final_hint is not "":
                final_hint = "{0}, {1}".format(final_hint, use_gsi_hint)
            else:
                final_hint = use_gsi_hint

        flex_query = flex_query_ph.format(flex_hint=final_hint)

        return flex_query


# ======================== tests =====================================================

    def test_flex_single_typemapping(self):

        self._load_emp_dataset(end=self.num_items)

        fts_index = self.create_fts_index(
            name="custom_index", source_name=self.bucket_name)
        self.generate_random_queries(fts_index.smart_query_fields)
        self.update_expected_fts_index_map(fts_index)
        if not self.is_index_present("default", "primary_gsi_index"):
            self.run_cbq_query("create primary index primary_gsi_index on default")
        failed_to_run_query, not_found_index_in_response, result_mismatch = self.run_queries_and_validate()
        self.cbcluster.delete_all_fts_indexes()

        if failed_to_run_query or not_found_index_in_response or result_mismatch:
            self.fail("Found queries not runnable: {0} or required index not found in the query resonse: {1} "
                      "or flex query and gsi query results not matching: {2}"
                      .format(failed_to_run_query, not_found_index_in_response, result_mismatch))
        else:
            self.log.info("All {0} queries passed".format(len(self.query_gen.fts_flex_queries)))

    def test_flex_multi_typemapping(self):

        self._load_emp_dataset(end=(self.num_items/2))
        self._load_wiki_dataset(end=(self.num_items/2))

        fts_index = self.create_fts_index(
            name="custom_index", source_name=self.bucket_name)
        self.generate_random_queries(fts_index.smart_query_fields)
        self.update_expected_fts_index_map(fts_index)
        if not self.is_index_present("default", "primary_gsi_index"):
            self.run_cbq_query("create primary index primary_gsi_index on default")
        failed_to_run_query, not_found_index_in_response, result_mismatch = self.run_queries_and_validate()
        self.cbcluster.delete_all_fts_indexes()

        if failed_to_run_query or not_found_index_in_response or result_mismatch:
            self.fail("Found queries not runnable: {0} or required index not found in the query resonse: {1} "
                      "or flex query and gsi query results not matching: {2}"
                      .format(failed_to_run_query, not_found_index_in_response, result_mismatch))
        else:
            self.log.info("All {0} queries passed".format(len(self.query_gen.fts_flex_queries)))

    def test_flex_default_typemapping(self):

        self._load_emp_dataset(end=self.num_items/2)
        self._load_wiki_dataset(end=(self.num_items/2))

        fts_index = self.create_fts_index(
            name="default_index", source_name=self.bucket_name)
        if not self.is_index_present("default", "primary_gsi_index"):
            self.run_cbq_query("create primary index primary_gsi_index on default")
        self.generate_random_queries()
        fts_index.smart_query_fields = self.query_gen.fields
        self.update_expected_fts_index_map(fts_index)
        failed_to_run_query, not_found_index_in_response, result_mismatch = self.run_queries_and_validate()
        self.cbcluster.delete_all_fts_indexes()

        if failed_to_run_query or not_found_index_in_response or result_mismatch:
            self.fail("Found queries not runnable: {0} or required index not found in the query resonse: {1} "
                      "or flex query and gsi query results not matching: {2}"
                      .format(failed_to_run_query, not_found_index_in_response, result_mismatch))
        else:
            self.log.info("All {0} queries passed".format(len(self.query_gen.fts_flex_queries)))


    def test_flex_single_typemapping_partial_sargability(self):

        self._load_emp_dataset(end=self.num_items)

        fts_index = self.create_fts_index(
            name="custom_index", source_name=self.bucket_name)
        self.generate_random_queries(fts_index.smart_query_fields)
        self.update_expected_fts_index_map(fts_index)
        if not self.is_index_present("default", "primary_gsi_index"):
            self.run_cbq_query("create primary index primary_gsi_index on default")
        gsi_fields = self.get_gsi_fields_partial_sargability()
        self.create_gsi_indexes(gsi_fields)
        self.generate_random_queries()
        failed_to_run_query, not_found_index_in_response, result_mismatch = self.run_queries_and_validate(partial_sargability = True)
        self.cbcluster.delete_all_fts_indexes()

        if failed_to_run_query or not_found_index_in_response or result_mismatch:
            self.fail("Found queries not runnable: {0} or required index not found in the query resonse: {1} "
                      "or flex query and gsi query results not matching: {2}"
                      .format(failed_to_run_query, not_found_index_in_response, result_mismatch))
        else:
            self.log.info("All {0} queries passed".format(len(self.query_gen.fts_flex_queries)))

    def test_flex_multi_typemapping_partial_sargability(self):

        self._load_emp_dataset(end=(self.num_items/2))
        self._load_wiki_dataset(end=(self.num_items/2))

        fts_index = self.create_fts_index(
            name="custom_index")
        self.update_expected_fts_index_map(fts_index)
        if not self.is_index_present("default", "primary_gsi_index"):
            self.run_cbq_query("create primary index primary_gsi_index on default")
        self.generate_random_queries(fts_index.smart_query_fields)
        gsi_fields = self.get_gsi_fields_partial_sargability()
        self.create_gsi_indexes(gsi_fields)
        self.generate_random_queries()
        failed_to_run_query, not_found_index_in_response, result_mismatch = self.run_queries_and_validate()
        self.cbcluster.delete_all_fts_indexes()

        if failed_to_run_query or not_found_index_in_response or result_mismatch:
            self.fail("Found queries not runnable: {0} or required index not found in the query resonse: {1} "
                      "or flex query and gsi query results not matching: {2}"
                      .format(failed_to_run_query, not_found_index_in_response, result_mismatch))
        else:
            self.log.info("All {0} queries passed".format(len(self.query_gen.fts_flex_queries)))

    def test_flex_single_typemapping_2_fts_indexes(self):
        self._load_emp_dataset(end=self.num_items)

        fts_index_1 = self.create_fts_index(
            name="custom_index_1", source_name=self.bucket_name)
        fts_index_2 = self.create_fts_index(
            name="custom_index_2", source_name=self.bucket_name)
        self.log.info("Editing custom index with new map...")
        fts_index_2.generate_new_custom_map(seed=fts_index_2.cm_id+10)
        fts_index_2.index_definition['uuid'] = fts_index_2.get_uuid()
        fts_index_2.update()
        smart_fields = self.merge_smart_fields(fts_index_1.smart_query_fields, fts_index_2.smart_query_fields)
        self.generate_random_queries(smart_fields)

        self.update_expected_fts_index_map(fts_index_1)
        self.update_expected_fts_index_map(fts_index_2)
        if not self.is_index_present("default", "primary_gsi_index"):
            self.run_cbq_query("create primary index primary_gsi_index on default")

        gsi_fields = self.get_gsi_fields_partial_sargability()
        self.create_gsi_indexes(gsi_fields)
        self.generate_random_queries()
        failed_to_run_query, not_found_index_in_response, result_mismatch = self.run_queries_and_validate(partial_sargability = True)
        self.cbcluster.delete_all_fts_indexes()

        if failed_to_run_query or not_found_index_in_response or result_mismatch:
            self.fail("Found queries not runnable: {0} or required index not found in the query resonse: {1} "
                      "or flex query and gsi query results not matching: {2}"
                      .format(failed_to_run_query, not_found_index_in_response, result_mismatch))
        else:
            self.log.info("All {0} queries passed".format(len(self.query_gen.fts_flex_queries)))

    def test_flex_with_napa_dataset(self):

        self._load_napa_dataset(end=self.num_items)

        fts_index = self.create_fts_index(
            name="default_index", source_name=self.bucket_name, doc_count=self.num_items)
        if not self.is_index_present("default", "primary_gsi_index"):
            self.run_cbq_query("create primary index primary_gsi_index on default")

        query_list = ['SELECT META().id FROM `default` {0} WHERE address.ecpdId="1" ORDER BY META().id LIMIT 100',
                      'SELECT META().id, email FROM `default` {0} WHERE address.ecpdId="3" OR address.applicationId=300'
                      ' ORDER BY email,META().id LIMIT 10',
                      'SELECT META().id, address.applicationId FROM `default` {0} WHERE address.ecpdId="3" AND'
                      ' address.deviceTypeId=9 ORDER BY address.applicationId,META().id LIMIT 100',
                      'SELECT META().id FROM `default` {0} WHERE (address.ecpdId="3" OR address.applicationId=300) AND '
                      '(address.deviceTypeId=9 OR address.deviceStatus=0) ORDER BY META().id LIMIT 100',
                      'SELECT META().id, address.applicationId FROM `default` {0} WHERE address.applicationId = 1 AND '
                      'address.deviceTypeId=9 AND address.deviceStatus=0 ORDER BY address.applicationId LIMIT 100',
                      'SELECT META().id FROM `default` {0} WHERE address.deviceTypeId=9 AND address.deviceStatus=0'
                      ' ORDER BY address.applicationId,META().id LIMIT 100',
                      'SELECT META().id FROM `default` {0} WHERE address.deviceStatus=0 ORDER BY META().id LIMIT 100',
                      'SELECT META().id, address.activationDate FROM `default` {0} WHERE address.ecpdId="1" ORDER BY'
                      ' address.activationDate,META().id LIMIT 100',
                      'SELECT META().id FROM default {0} WHERE ( ( ( ( ( email LIKE "A%") OR '
                      '( ANY v IN devices SATISFIES v LIKE "2%" END)) OR '
                      '( first_name > "Karianne" AND first_name <= "Qarianne")) OR ( routing_number = 12160)) OR '
                      '( address.activationDate BETWEEN "1995-10-10T21:22:00" AND "2020-05-09T20:08:02.462692")) '
                      'ORDER BY address.city,META().id LIMIT 100',
                      'SELECT META().id, company_name FROM default {0} WHERE (( email = "Aaron.Jaskolski18@yahoo.com") '
                      'AND ( ANY v IN children SATISFIES v.first_name = "Raven" END)) OR '
                      '(( company_code > "IMWW" AND company_code <= "D3IHO") AND ( routing_number = 67473) OR '
                      '( address.activationDate BETWEEN "2019-10-10T21:22:00" AND "2020-05-09T20:08:02.462692")) '
                      'ORDER BY address.activationDate,META().id OFFSET 500 LIMIT 100',
                      'SELECT first_name, last_name, email FROM default {0} WHERE '
                      '( ( SOME v IN children SATISFIES v.first_name LIKE "R%" END) AND '
                      '( age > 20 AND age < 40)) OR '
                      '(( dob BETWEEN "1994-12-08T01:19:00" AND "2020-05-09T20:08:02.469127") AND isActive = FALSE) '
                      'OR (address.deviceTypeId > 3 AND ISNUMBER(address.deviceTypeId)) '
                      'ORDER BY address.activationDate,META().id OFFSET 500 LIMIT 100',
                      'SELECT first_name, last_name, email, address.country FROM default {0} WHERE '
                      'ANY c IN children SATISFIES c.gender = "F" AND (c.age > 5 AND c.age <15) '
                      'OR c.first_name LIKE "a%" END ORDER BY address.country,META().id OFFSET 500 LIMIT 100']

        failed_to_run_query, not_found_index_in_response, result_mismatch = self.run_query_and_validate(query_list)
        if failed_to_run_query or not_found_index_in_response or result_mismatch:
            self.fail("Found queries not runnable: {0} or required index not found in the query resonse: {1} "
                      "or flex query and gsi query results not matching: {2}"
                      .format(failed_to_run_query, not_found_index_in_response, result_mismatch))
        else:
            self.log.info("All {0} queries passed".format(len(query_list)))
