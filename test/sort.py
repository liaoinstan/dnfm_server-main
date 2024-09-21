# 定义比较函数
def custom_sort(t):
    return  t[1],t[0]

# 列表中的元组
lst = [(3, 2), (1, 5), (2, 3), (1, 2), (3, 1),(2,9)]

# 对列表进行自定义排序
sorted_lst = sorted(lst, key=custom_sort)

print(sorted_lst)
