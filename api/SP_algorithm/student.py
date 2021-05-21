import copy


def check_budget(order):
    sum_bidding = 0
    order_values = list(order.values())
    for i in range(len(order_values)):
        sum_bidding += order_values[i]

    if sum_bidding > 500:
        raise Exception("Sorry, the sum of bidding is can't be summarized above 500")

    else:
        return True


def create_ordinal_order(order):
    count = 1
    ordinal = list(order.values())
    course_names = list(order.keys())
    for i in range(len(ordinal)):
        ind = ordinal.index(max(ordinal))
        ordinal[ind] = count
        count += 1

    output = copy.deepcopy(order)
    for i in range(len(output)):
        output[course_names[i]] = ordinal[i]

    return output


class Student:

    def __init__(self, id, need_number , student_office,  cardinal_order, enrolled_or_not):
        if check_budget(self.cardinal_order):
            self.id = id
            self.need_to_enroll = need_number
            self.enrolled_num = 0
            self.cardinal_order = copy.deepcopy(cardinal_order)
            self.changeable_cardinal_order = cardinal_order
            self.enrolled_or_not = enrolled_or_not
            self.ordinal_order = {}
            self.cardinal_utility = 0
            self.ordinal_utility = 0
            self.enrolled_first_phase = False
            self.office = student_office


    def get_name(self):
        return self.name

    def get_ordinal(self):
        return self.ordinal_order

    def get_cardinal(self):
        return self.cardinal_order

    def get_cardinal_utility(self):
        return self.cardinal_utility

    def get_need_to_enroll(self):
        return self.need_to_enroll

    def get_enrolment_status(self):
        return self.enrolled_or_not

    def get_next_preference(self):
        cardinal_value = list(self.changeable_cardinal_order.values())
        cardinal_keys = list(self.changeable_cardinal_order.keys())
        max_value_index = cardinal_value.index(max(cardinal_value))
        course_name = cardinal_keys[max_value_index]
        self.changeable_cardinal_order[course_name] = 0
        cardinal_value[max_value_index] = 0
        max_value_index = cardinal_value.index(max(cardinal_value))
        return {cardinal_keys[max_value_index]: cardinal_value[max_value_index]}

    def have_another_preference(self):
        cardinal_value = list(self.changeable_cardinal_order.values())
        if cardinal_value.count(0) == len(cardinal_value):
            return True

        else:
            return False


    def get_next_preference_without_change(self):
        cardinal_value = list(self.changeable_cardinal_order.values())
        cardinal_keys = list(self.changeable_cardinal_order.keys())
        max_value_index = cardinal_value.index(max(cardinal_value))
        return {cardinal_keys[max_value_index]: cardinal_value[max_value_index]}

    def get_number_of_enrollments(self):
        return self.enrolled_num

    def add_gap(self, gap):
        cardinal_value = list(self.changeable_cardinal_order.values())
        cardinal_keys = list(self.changeable_cardinal_order.keys())
        max_value_index = cardinal_value.index(max(cardinal_value))
        course_name = cardinal_keys[max_value_index]
        self.changeable_cardinal_order[course_name] = 0
        cardinal_value[max_value_index] = 0
        if cardinal_value.count(0) != len(cardinal_value):
            max_value_index = cardinal_value.index(max(cardinal_value))
            course_name = cardinal_keys[max_value_index]
            self.changeable_cardinal_order[course_name] = cardinal_value[max_value_index] + gap

    def get_current_highest_bid(self):
        cardinal_value = list(self.changeable_cardinal_order.values())
        index = cardinal_value.index(max(cardinal_value))
        return cardinal_value[index]

    def current_highest_ordinal(self, course_name):
        return self.ordinal_order[course_name]

    def got_enrolled(self, course_name):
        if self.need_to_enroll > 0 and self.enrolled_or_not[course_name] == 0:
            self.need_to_enroll -= 1
            self.cardinal_utility += self.changeable_cardinal_order[course_name]
            self.changeable_cardinal_order[course_name] = 0
            self.enrolled_or_not[course_name] = 1
            self.enrolled_num += 1
            self.ordinal_utility += len(self.ordinal_order) - self.ordinal_order[course_name]+1

        elif self.enrolled_or_not[course_name] == 1:
            print("Student: ", self.name, ", is already enrolled to the course: ", course_name)

        else:
            print("Student: ", self.name, " got to the limit of courses enrollment")

    def to_string(self):
        print("Student name:", self.name, ", The cardinal order is: ", self.cardinal_order, "\n"  "The ordinal is: ",
              self.ordinal_order, "\n", "The courses that: ", self.name, " enrolled are: ", self.enrolled_or_not, "\n"
              "The cardinal utility is: ", self.cardinal_utility, ", The ordinal utility is: ", self.ordinal_utility)
