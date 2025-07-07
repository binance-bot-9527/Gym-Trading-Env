import numpy as np

class History:
    # 历史记录类，用于存储和管理环境运行过程中的各种信息。
    def __init__(self, max_size = 10000):
        # 初始化历史记录。
        # max_size: 历史记录的最大容量。
        self.height = max_size
    def set(self, **kwargs):
        # 设置历史记录的初始状态和列名。
        # kwargs: 键值对，表示要记录的初始数据。
        # 将输入展平以放入np.array中
        self.columns = []
        for name, value in kwargs.items():
            if isinstance(value, list):
                self.columns.extend([f"{name}_{i}" for i in range(len(value))])
            elif isinstance(value, dict):
                self.columns.extend([f"{name}_{key}" for key in value.keys()])
            else:
            # 如果列不匹配，则抛出错误。
                self.columns.append(name)
        
        self.width = len(self.columns)
        self.history_storage = np.zeros(shape=(self.height, self.width), dtype= 'O')
        self.size = 0
        self.add(**kwargs)
    def add(self, **kwargs):
        # 向历史记录中添加新的数据。
        # kwargs: 键值对，表示要添加的数据。
        values = []
        columns = []
        for name, value in kwargs.items():
            if isinstance(value, list):
                columns.extend([f"{name}_{i}" for i in range(len(value))])
                values.extend(value[:])
            elif isinstance(value, dict):
                columns.extend([f"{name}_{key}" for key in value.keys()])
                values.extend(list(value.values()))
            else:
                columns.append(name)
                values.append(value)

        if columns == self.columns:
            # 检查新数据的列是否与现有列匹配。
            # 如果匹配，则将数据添加到存储中。
            self.history_storage[self.size, :] = values
            self.size = min(self.size+1, self.height)
        else:
            raise ValueError(f"Make sur that your inputs match the initial ones... Initial ones : {self.columns}. New ones {columns}")
    def __len__(self):
        # 返回历史记录中当前存储的条目数量。
        return self.size
    def __getitem__(self, arg):
        # 允许通过索引或切片访问历史记录中的数据。
        # arg: 可以是列名、索引或两者的组合。
        if isinstance(arg, tuple):
            column, t = arg
        # 解析列名和时间索引。
            # 如果arg是元组，表示按列和时间索引访问。
            try:
                column_index = self.columns.index(column)
            except ValueError as e:
            # 如果指定的特征不存在，则抛出错误。
                # 如果指定的特征不存在，则抛出错误。
                # 如果指定的特征不存在，则抛出错误。
                raise ValueError(f"Feature {column} does not exist ... Check the available features : {self.columns}")
            return self.history_storage[:self.size][t, column_index]
        if isinstance(arg, int):
            # 如果arg是整数，表示按时间索引访问。
            t = arg
            return dict(zip(self.columns, self.history_storage[:self.size][t]))
        if isinstance(arg, str):
            # 如果arg是字符串，表示按列名访问。
            column = arg
            try:
                column_index = self.columns.index(column)
            except ValueError as e:
                raise ValueError(f"Feature {column} does not exist ... Check the available features : {self.columns}")
            return self.history_storage[:self.size][:, column_index]
        if isinstance(arg, list):
            # 如果arg是列表，表示按多个列名访问。
            columns = arg
            column_indexes = []
            for column in columns:
                try:
                    column_indexes.append(self.columns.index(column))
                except ValueError as e:
                    # 如果指定的特征不存在，则抛出错误。
                    raise ValueError(f"Feature {column} does not exist ... Check the available features : {self.columns}")
            return self.history_storage[:self.size][:, column_indexes]

    def __setitem__(self, arg, value):
        # 允许设置历史记录中特定位置的值。
        # arg: 列名和时间索引的元组。
        # value: 要设置的新值。
        column, t = arg
        try:
            column_index = self.columns.index(column)
        except ValueError as e:
            raise ValueError(f"Feature {column} does not exist ... Check the available features : {self.columns}")
        self.history_storage[:self.size][t, column_index] = value