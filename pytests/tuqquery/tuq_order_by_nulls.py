import copy
import math

from .tuq import QueryTests


class OrderByNullsTests(QueryTests):

    def setUp(self):
        super(OrderByNullsTests, self).setUp()
        self.numbers = [1, 3, 5, 7, 9, 10, 0, 2, 4, 6, 8, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27,
                        28,
                        29, 30, 31, 32, 33, 34, 35, 36, 37, 1, 3, 5, 7, 9, 10, 0, 2, 4, 6, 8, 13, 14, 15, 16, 17, 18,
                        19,
                        20, 21, 22, 23, 24]
        self.datatypes = ['int', 'float', 'varchar', 'bool']
        self.where = ['', ' WHERE bool_field=True ']
        self.maybe_asc = [' ', ' ASC ']

        self.maybe_nulls_first = [' ', ' NULLS FIRST ']
        self.maybe_nulls_last = [' ', ' NULLS LAST ']

        self.primary_idx = {'name': '#primary', 'bucket': "temp_bucket", 'fields': [], 'state': 'online',
                            'using': self.index_type.lower(), 'is_primary': True}
        self.idx_1 = {'name': "ix1", 'bucket': "temp_bucket", 'fields': [("int_field", 0)], 'state': "online",
                      'using': self.index_type.lower(), 'is_primary': False}
        self.idx_2 = {'name': "ix2", 'bucket': "temp_bucket", 'fields': [("float_field", 0)], 'state': "online",
                      'using': self.index_type.lower(), 'is_primary': False}
        self.idx_3 = {'name': "ix3", 'bucket': "temp_bucket", 'fields': [("varchar_field", 0)], 'state': "online",
                      'using': self.index_type.lower(), 'is_primary': False}
        self.idx_4 = {'name': "ix4", 'bucket': "temp_bucket", 'fields': [("bool_field", 0)], 'state': "online",
                      'using': self.index_type.lower(), 'is_primary': False}

        self.indexes = [self.primary_idx, self.idx_1, self.idx_3]
        if self.test_buckets == 'default':
            self.test_buckets = 'temp_bucket'
        self.query_bucket = self.get_query_buckets(check_all_buckets=True)[0]

    def tearDown(self):
        super(OrderByNullsTests, self).tearDown()

    def suite_setUp(self):
        super(OrderByNullsTests, self).suite_setUp()

    def suite_tearDown(self):
        super(OrderByNullsTests, self).suite_tearDown()

    def run_all(self):
        self.test_order_by_col_maybe_asc_maybe_nulls_first()
        self.test_order_by_col_maybe_asc_nulls_last()
        self.test_order_by_col_desc_maybe_nulls_last()
        self.test_order_by_col_desc_nulls_first()

    ''' select field from bucket [where | ] order by field [ASC | ] [NULLS FIRST | ]'''

    def test_order_by_col_maybe_asc_maybe_nulls_first(self):
        self._load_test_data()
        test_dict = dict()
        count = 0

        for datatype in self.datatypes:
            for asc in self.maybe_asc:
                for nulls in self.maybe_nulls_first:
                    for where_clause in self.where:
                        query = "select " + datatype + "_field from " + self.query_bucket + " " + where_clause + \
                                " order by " + datatype + "_field " + asc + nulls
                        lambda1 = lambda x, y=datatype, z=query: self.assertEqual(True,
                                                                                  self._check_order_nulls_first_asc(
                                                                                      x['q_res'][0], y), z)
                        test_dict["%d-default" % count] = {"indexes": self.indexes,
                                                           "pre_queries": [],
                                                           "queries": [query],
                                                           "post_queries": [],
                                                           "asserts": [lambda1],
                                                           "cleanups": []}
                        count += 1

        try:
            self.query_runner(test_dict)
        finally:
            self._unload_test_data()

    ''' select field from bucket [where | ] order by field [ASC | ] NULLS LAST'''

    def test_order_by_col_maybe_asc_nulls_last(self):
        self._load_test_data()
        test_dict = dict()
        count = 0

        for datatype in self.datatypes:
            for asc in self.maybe_asc:
                for where_clause in self.where:
                    query = "select " + datatype + "_field from " + self.query_bucket + " " + where_clause + \
                            " order by " + datatype + "_field " + asc + " NULLS LAST"
                    lambda1 = lambda x, y=datatype, z=query: self.assertEqual(True, self._check_order_nulls_last_asc(
                        x['q_res'][0], y), z)
                    test_dict["%d-default" % count] = {"indexes": self.indexes,
                                                       "pre_queries": [],
                                                       "queries": [query],
                                                       "post_queries": [],
                                                       "asserts": [lambda1],
                                                       "cleanups": []}
                    count += 1

        try:
            self.query_runner(test_dict)
        finally:
            self._unload_test_data()

    ''' select field from bucket [where | ] order by field DESC [NULLS LAST | ]'''

    def test_order_by_col_desc_maybe_nulls_last(self):
        self._load_test_data()
        test_dict = dict()
        count = 0

        for datatype in self.datatypes:
            for nulls in self.maybe_nulls_last:
                for where_clause in self.where:
                    query = "select " + datatype + "_field from " + self.query_bucket + " " + where_clause + \
                            " order by " + datatype + "_field DESC " + nulls
                    lambda1 = lambda x, y=datatype, z=query: self.assertEqual(True, self._check_order_nulls_last_desc(
                        x['q_res'][0], y), z)
                    test_dict["%d-default" % count] = {"indexes": self.indexes,
                                                       "pre_queries": [],
                                                       "queries": [query],
                                                       "post_queries": [],
                                                       "asserts": [lambda1],
                                                       "cleanups": []}
                    count += 1

        try:
            self.query_runner(test_dict)
        finally:
            self._unload_test_data()

    ''' select field from bucket [where | ] order by field DESC NULLS FIRST '''

    def test_order_by_col_desc_nulls_first(self):
        self._load_test_data()
        test_dict = dict()
        count = 0

        for datatype in self.datatypes:
            for where_clause in self.where:
                query = "select " + datatype + "_field from " + self.query_bucket + " " + where_clause + \
                        " order by " + datatype + "_field DESC NULLS FIRST"
                lambda1 = lambda x, y=datatype, z=query: self.assertEqual(True, self._check_order_nulls_first_desc(
                    x['q_res'][0], y), z)
                test_dict["%d-default" % count] = {"indexes": self.indexes,
                                                   "pre_queries": [],
                                                   "queries": [query],
                                                   "post_queries": [],
                                                   "asserts": [lambda1],
                                                   "cleanups": []}
                count += 1

        try:
            self.query_runner(test_dict)
        finally:
            self._unload_test_data()

    ###################################################################################################################
    #                               Check functions, compare couchbase ordering with natural ordering
    ###################################################################################################################
    def _check_order_nulls_last_asc(self, result, datatype):
        non_null_results = []

        if len(result['results']) == 0:
            return False

        cur_result = result['results'][0]

        for i in range(1, len(result['results'])):
            if str(cur_result) != '{}' and cur_result[datatype + '_field'] is not None:
                non_null_results.append(cur_result[datatype + '_field'])
                cur_result = result['results'][i]
                continue
            elif str(cur_result) == '{}':
                if str(result['results'][i]) == '{}' or result['results'][i][datatype + '_field'] is None:
                    cur_result = result['results'][i]
                    continue
                else:
                    return False
            elif cur_result[datatype + '_field'] is None:
                if str(result['results'][i]) == '{}' or result['results'][i][datatype + '_field'] is not None:
                    return False
                else:
                    cur_result = result['results'][i]

        copy_results = copy.copy(non_null_results)
        copy_results.sort(reverse=False)
        for i in range(len(non_null_results)):
            if non_null_results[i] != copy_results[i]:
                return False

        return True

    def _check_order_nulls_last_desc(self, result, datatype):
        non_null_results = []

        if len(result['results']) == 0:
            return False

        cur_result = result['results'][0]

        for i in range(1, len(result['results'])):
            if str(cur_result) != '{}' and cur_result[datatype + '_field'] is not None:
                non_null_results.append(cur_result[datatype + '_field'])
                cur_result = result['results'][i]
                continue
            elif str(cur_result) == '{}':
                if str(result['results'][i]) == '{}':
                    cur_result = result['results'][i]
                    continue
                else:
                    return False
            elif cur_result[datatype + '_field'] is None:
                if str(result['results'][i]) == '{}' or result['results'][i][datatype + '_field'] is None:
                    cur_result = result['results'][i]
                else:
                    return False

        copy_results = copy.copy(non_null_results)
        copy_results.sort(reverse=True)
        for i in range(len(non_null_results)):
            if non_null_results[i] != copy_results[i]:
                return False

        return True

    def _check_order_nulls_first_asc(self, result, datatype):
        non_null_results = []

        if len(result['results']) == 0:
            return False

        cur_result = result['results'][0]

        for i in range(1, len(result['results'])):
            if str(cur_result) == '{}':
                cur_result = result['results'][i]
                continue
            elif cur_result[datatype + '_field'] is None:
                if str(result['results'][i]) == '{}':
                    return False
                else:
                    cur_result = result['results'][i]
                    continue
            else:
                if str(result['results'][i]) == '{}' or result['results'][i][datatype + '_field'] is None:
                    return False
                else:
                    non_null_results.append(cur_result[datatype + '_field'])
                    cur_result = result['results'][i]

        sorted_results = copy.copy(non_null_results)
        sorted_results.sort(reverse=False)
        for i in range(len(non_null_results)):
            if non_null_results[i] != sorted_results[i]:
                return False

        return True

    def _check_order_nulls_first_desc(self, result, datatype):
        non_null_results = []

        if len(result['results']) == 0:
            return False
        cur_result = result['results'][0]
        for i in range(1, len(result['results'])):
            if str(cur_result) == '{}':
                if str(result['results'][i]) != '{}' and result['results'][i][datatype + '_field'] is None:
                    return False
                else:
                    cur_result = result['results'][i]
                    continue
            elif cur_result[datatype + '_field'] is None:
                cur_result = result['results'][i]
                continue
            else:
                if str(result['results'][i]) == '{}' or result['results'][i][datatype + '_field'] is None:
                    return False
                else:
                    non_null_results.append(cur_result[datatype + '_field'])
                    cur_result = result['results'][i]

        sorted_results = copy.copy(non_null_results)
        sorted_results.sort(reverse=True)
        for i in range(len(non_null_results)):
            if non_null_results[i] != sorted_results[i]:
                return False

        return True

    ####################################################################################################################
    #           Load/Cleanup of test data
    ####################################################################################################################
    def _load_test_data(self):
        temp_bucket_params = self._create_bucket_params(server=self.master, size=self.bucket_size,
                                                        replicas=self.num_replicas, bucket_type=self.bucket_type,
                                                        enable_replica_index=self.enable_replica_index,
                                                        eviction_policy=self.eviction_policy, lww=self.lww)
        self.cluster.create_standard_bucket(self.test_buckets, 11222, temp_bucket_params)

        for bucket in self.buckets:
            self.cluster.bucket_flush(self.master, bucket=bucket, timeout=self.wait_timeout * 5)
        # Adding sleep after flushing buckets (see CBQE-5838)
        self.sleep(210)

        for i in range(len(self.numbers)):
            int_val = self.numbers[i]
            float_val = self.numbers[i] * math.pi
            varchar_val = "string" + str(self.numbers[i])
            bool_val = True

            if i % 2 == 0:
                int_val = 'NULL'
                bool_val = False
            if i % 3 == 0:
                float_val = 'NULL'
            if i % 5 == 0:
                varchar_val = 'NULL'
            if i % 11 == 0:
                int_val = ''
            if i % 13 == 0:
                float_val = ''
            if i % 17 == 0:
                varchar_val = ''

            query = "insert into " + self.query_bucket + " values ('key_" + str(i) + "', {"

            int_field_insert = "'int_field': " + str(int_val) + ","
            if int_val == '':
                int_field_insert = ''

            float_field_insert = "'float_field': " + str(float_val) + ","
            if float_val == '':
                float_field_insert = ''

            varchar_field_insert = "'varchar_field': '" + varchar_val + "',"
            if varchar_val == '':
                varchar_field_insert = ''

            bool_field_insert = "'bool_field': " + str(bool_val)
            if bool_val == '':
                bool_field_insert = ''

            query += " " + int_field_insert + float_field_insert + varchar_field_insert + bool_field_insert + "})"
            self.run_cbq_query(query)

        self.run_cbq_query('CREATE PRIMARY INDEX `#primary` ON ' + self.query_bucket)
        self.run_cbq_query('CREATE INDEX ix1 ON ' + self.query_bucket + '(int_field);')
        self.run_cbq_query('CREATE INDEX ix2 ON ' + self.query_bucket + '(float_field);')
        self.run_cbq_query('CREATE INDEX ix3 ON ' + self.query_bucket + '(varchar_field);')
        self.run_cbq_query('CREATE INDEX ix4 ON ' + self.query_bucket + '(bool_field);')

    def _unload_test_data(self):
        self.cluster.bucket_delete(self.master, self.test_buckets)

    def test_order_by_param(self):
        self.run_cbq_query('DELETE FROM system:prepareds WHERE name = "v5"')
        self.run_cbq_query('DELETE FROM default WHERE meta().id in ["t1","t2","t3"]')
        self.run_cbq_query('insert into default (key,value) values("t1",{"a":1}),("t2",{"a":2}),("t3",{"a":null})')
        self.run_cbq_query(f'prepare v5 from select * from default as d where meta().id in ["t1","t2","t3"] order by d.[$c] $o nulls $n')

        with self.subTest('ASC/FIRST'):
            expected = self.run_cbq_query(f'select * from default as d where meta().id in ["t1","t2","t3"] order by a asc nulls first')
            actual = self.run_cbq_query('execute v5 using {"c": "a", "o":"asc", "n":"first"}')
            self.assertEqual(actual['results'], expected['results'])
        with self.subTest('ASC/LAST'):
            expected = self.run_cbq_query(f'select * from default as d where meta().id in ["t1","t2","t3"] order by a asc nulls last')
            actual = self.run_cbq_query('execute v5 using {"c": "a", "o":"asc", "n":"last"}')
            self.assertEqual(actual['results'], expected['results'])
        with self.subTest('DESC/FIRST'):
            expected = self.run_cbq_query(f'select * from default as d where meta().id in ["t1","t2","t3"] order by a desc nulls first')
            actual = self.run_cbq_query('execute v5 using {"c": "a", "o":"desc", "n":"first"}')
            self.assertEqual(actual['results'], expected['results'])
        with self.subTest('DESC/LAST'):
            expected = self.run_cbq_query(f'select * from default as d where meta().id in ["t1","t2","t3"] order by a desc nulls last')
            actual = self.run_cbq_query('execute v5 using {"c": "a", "o":"desc", "n":"last"}')
            self.assertEqual(actual['results'], expected['results'])
        with self.subTest('DESC/MISSING'):
            expected = self.run_cbq_query(f'select * from default as d where meta().id in ["t1","t2","t3"] order by a desc nulls last')
            actual = self.run_cbq_query('execute v5 using {"c": "a", "o":"desc"}')
            self.assertEqual(actual['results'], expected['results'])
        with self.subTest('ASC/MISSING'):
            expected = self.run_cbq_query(f'select * from default as d where meta().id in ["t1","t2","t3"] order by a asc nulls first')
            actual = self.run_cbq_query('execute v5 using {"c": "a", "o":"asc"}')
            self.assertEqual(actual['results'], expected['results'])
        with self.subTest('MISSING/MISSING'):
            expected = self.run_cbq_query(f'select * from default as d where meta().id in ["t1","t2","t3"] order by a asc nulls first')
            actual = self.run_cbq_query('execute v5 using {"c": "a"}')
            self.assertEqual(actual['results'], expected['results'])
