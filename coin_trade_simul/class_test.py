class test_Class():
    # class 자체에서 가지는 하나의 값
    class_var = 0

    # self 이하는 객체 생성 이후 객체마다 별도로 가지게 되는 값
    def __init__(self):
        self.v_a = 0

    def set_a(self, n):
        self.v_a = n

    @property
    def get_classvar(cls):
        return cls.class_var

    @classmethod
    def increment_classvar(cls):
        cls.class_var += 1

if __name__ == '__main__':
    a = test_Class()
    b = test_Class()

    a.set_a(33)
    b.set_a(111)

    print(a.v_a, b.v_a)

    print(a.get_classvar)

    a.increment_classvar()
    print(b.get_classvar)

    b.increment_classvar()
    print(a.get_classvar)

    print(test_Class.class_var)
