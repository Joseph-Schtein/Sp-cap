from copy import deepcopy

from .course import Course
from .course_group import Course_group
from .student import Student
from collections import OrderedDict

def create_matrix(dic_list, course_list, row_number, column_number):
    list_of_name = ["" for i in range(row_number)]
    list_of_ranking = [0 for i in range(row_number * column_number)]
    counter1 = 0
    counter2 = 0
    for i in range(row_number):
        for j in range(column_number):
            if j % row_number == 0:
                list_of_name[counter1] = list(dic_list[i][j].values())[0]

            list_of_ranking[counter2] = list(dic_list[i][j].values())[2]
            counter2 += 1

        counter1 += 1

    counter = 0
    course_price = {}
    for i in range(row_number):
        student_bidding = {}
        for j in range(column_number):
            student_bidding[course_list[j]] = list_of_ranking[counter]
            counter += 1

        course_price[list_of_name[i]] = student_bidding

    return course_price

'''
def create_students(fixed, course_names):
    student_name_list = list(fixed.keys())
    student_rank = list(fixed.values())
    student_list = []
    course_take = {}
    for i in range(len(course_names)):
        course_take[course_names[i]] = 0
    for i in range(len(fixed)):
        course_tmp = deepcopy(course_take)
        stu = Student(student_name_list[i], student_rank[i], course_tmp)
        student_list.append(stu)
    return student_list
def create_courses(fixed):
    tmp = list(fixed.values())
    courses_name_list = list(tmp[0].keys())
    course_list = []
    for i in range(len(courses_name_list)):
        if i == 0:
            cou = Course(courses_name_list[i], 3, 2, ["c"])
            course_list.append(cou)
        elif i == 2:
            cou = Course(courses_name_list[i], 3, 2, ["a"])
            course_list.append(cou)
        else:
            cou = Course(courses_name_list[i], 3, 2, [])
            course_list.append(cou)
    return course_list
'''

def check_overlap(student_object, course_object):
    overlap_courses = course_object.get_overlap_list()
    if len(overlap_courses) > 0:
        output = True
        enroll_status = student_object.get_enrolment_status()
        for overlap in range(len(overlap_courses)):
            if output:
                course_name = overlap_courses[overlap]
                check = enroll_status[course_name.get_name()]
                if check == 1:
                    student_object.get_next_preference()
                    if output:
                        output = False

            return output

    else:
        return True


def ready_to_new_round(student_list, student_names, ranks):
    _data = {}
    for i in range(len(ranks)):
        ranks[i] = student_list[i].get_changeable_cardinal()
        course_names = list(ranks[i].keys())
        vector_rank = list(ranks[i].values())
        index = vector_rank.index(max(vector_rank))
        _data[student_names[i]] = {course_names[index]: vector_rank[index]}

    return _data


def second_phase(ranks, student_list, elective_course_list, round_number, group_course):
    max_enrolled = 0
    need_to_enroll = [False for i in range(len(student_list))]
    for index in range(len(student_list)):
        if max_enrolled < student_list[index].get_number_of_enrollments():
            max_enrolled = student_list[index].get_number_of_enrollments()

    if need_to_enroll.count(True) != len(need_to_enroll):
        while need_to_enroll.count(True) != len(need_to_enroll):
            for index in range(len(need_to_enroll)):
                if not ((student_list[index].have_another_preference()) or\
                                        (student_list[index].get_number_of_enrollments() == round_number ) or\
                                        (student_list[index].get_next_preference_without_change() == 0)):
                    need_to_enroll[index] = True

            tmp_student_list = []
            tmp_student_names_list = []
            tmp_ranks = []


            for stu in range(len(student_list)):
                if student_list[stu].get_number_of_enrollments() < max_enrolled and need_to_enroll[stu] == True:
                    tmp_student_list.append(student_list[stu])
                    tmp_student_names_list.append(student_list[stu].get_id())
                    tmp_ranks.append(ranks[stu])

            tmp_data = ready_to_new_round(tmp_student_list, tmp_student_names_list, tmp_ranks)

            if len(tmp_student_list) > 0:
                enroll_students(tmp_data, tmp_student_list, elective_course_list, group_course)
            for index in range(len(student_list)):
                if student_list[index].get_number_of_enrollments() or\
                                student_list[index].get_number_of_enrollments() == round_number  or\
                                student_list[index].get_next_preference_without_change() == 0:
                    need_to_enroll[index] = False

            if need_to_enroll.count(False) == len(need_to_enroll):
                for index in range(len(student_list)):
                    need_to_enroll[index] = True


    elif need_to_enroll.count(True) == len(need_to_enroll) and round_number < max_enrolled:
        while enroll_list.count(max_enrolled) == len(enroll_list) and round_number  < max_enrolled:
            for stu in range(len(student_list)):
                _data[student_list[stu].get_id()] = student_list[stu].get_next_preference()
            enroll_students(_data, student_list, elective_course_list, group_course)




def there_is_a_tie(student_object):
    start_end = [0 for i in range(len(student_object))]
    counter = 1
    for index in range(len(student_object)-1):
        if student_object[index].get_current_highest_bid() == student_object[index+1].get_current_highest_bid():
            start_end[index] = counter
            start_end[index+1] = counter

        elif student_object[index].get_current_highest_bid() != student_object[index+1].get_current_highest_bid()\
                and start_end[index] != 0:
            counter += 1

    return start_end


def sort_tie_breaker(student_object_try, check, course_name):
    max_value = max(check)
    for i in range(1, max_value+1):
        min_index = check.index(i)
        max_index = len(check) - check[::-1].index(i) - 1    # sort other way around and find the index of the element i
        tie_student = student_object_try[min_index:max_index+1]
        fixed_tie_student = sorted(tie_student, key=lambda x: (x.get_number_of_enrollments(), x.current_highest_ordinal(course_name)))
        student_object_try[min_index:max_index] = fixed_tie_student


def enroll_students(_data, student_list, elective_course_list, group_course):
    amount_of_bidrs = {}
    student_element = {}
    for co in elective_course_list:
        amount_of_bidrs[co.get_name()] = []
        student_element[co.get_name()] = []

    course_bid = list(_data.values())
    for i in range(len(student_list)):
        if student_list[i].get_current_highest_bid() > 0:
            course = list(course_bid[i].keys())
            amount_of_bidrs[course[0]].append(student_list[i].get_id())
            student_element[course[0]].append(student_list[i])

    j = -1
    for key, value in amount_of_bidrs.items():
        j += 1
        if len(value) > 0:
            try_to_enroll = amount_of_bidrs[key]
            student_object_try = student_element[key]




            if key == elective_course_list[j].get_name():
                if elective_course_list[j].can_be_enroll(len(try_to_enroll)):
                    if len(try_to_enroll) > 0:  # when we can enroll everyone
                        for need_to in range(len(try_to_enroll)):
                            if check_overlap(student_object_try[need_to], elective_course_list[j]):  # Enroll student if he dose
                                # not have overlap course to course_list[j]
                                elective_course_list[j].student_enrollment(try_to_enroll[need_to], student_object_try[need_to])
                                student_object_try[need_to].got_enrolled(elective_course_list[j].get_name())


                            else:  # If the student enrolled already to overlap course over course_list[j]
                                #gap = elective_course_list[j].get_lowest_bid() - \
                                #      student_object_try[need_to].get_current_highest_bid()

                                #student_object_try[need_to].add_gap(gap)

                                _data[try_to_enroll[need_to]] = \
                                    student_object_try[need_to].get_next_preference_without_change()


                elif elective_course_list[j].get_capacity() == 0:  # If the capacity is zero
                    counter = 0
                    for stu in range(len(student_object_try)):
                        if student_object_try[stu].get_need_to_enroll() != 0:

                                    #gap = elective_course_list[j].get_lowest_bid() - \
                                    #      student_object_try[stu].get_current_highest_bid()

                                    #student_object_try[stu].add_gap(gap)

                            _data[try_to_enroll[counter]] = \
                                student_object_try[stu].get_next_preference_without_change()
                            counter += 1


                elif not elective_course_list[j].can_be_enroll(len(try_to_enroll)):
                    # If the capacity is not let to enroll all student who put bid over that course
                    student_object_try = sorted(student_object_try, key=lambda x: x.get_current_highest_bid(), reverse=True)

                    check = there_is_a_tie(student_object_try)
                    if check.count(0) == len(check):    # In case there isn't a tie between student bids
                        for stu in range(len(student_object_try)):
                            if elective_course_list[j].get_capacity() > 0 and check_overlap(student_object_try[stu], elective_course_list[j]):
                                elective_course_list[j].student_enrollment(student_object_try[stu].get_id(), student_object_try[stu])
                                student_object_try[stu].got_enrolled(elective_course_list[j].get_name())


                            else:
                                # If there is a student such that want to enroll to course but is overlap or have zero
                                # capacity

                                #gap = elective_course_list[j].get_lowest_bid() - \
                                #      student_object_try[stu].get_current_highest_bid()

                                 #student_object_try[stu].add_gap(gap)

                                _data[student_object_try[stu].get_id()] = \
                                    student_object_try[stu].get_next_preference_without_change()

                    else:   # In case there is a tie between student bids we break the tie by there ordinal order
                        sort_tie_breaker(student_object_try, check, elective_course_list[j].get_name())
                        for stu in range(len(student_object_try)):
                            if elective_course_list[j].get_capacity() > 0 and check_overlap(student_object_try[stu], elective_course_list[j]):

                                # If there is a place to enroll student stu
                                elective_course_list[j].student_enrollment(student_object_try[stu].get_id(),
                                                              student_object_try[stu])
                                student_object_try[stu].got_enrolled(elective_course_list[j].get_name())

                            else:
                                # If there is a student such that want to enroll to course but is overlap or have zero
                                # capacity

                                #gap = elective_course_list[j].get_lowest_bid() - \
                                #    student_object_try[stu].get_current_highest_bid()

                                #student_object_try[stu].add_gap(gap)

                                _data[student_object_try[stu].get_id()] = \
                                    student_object_try[stu].get_next_preference_without_change()



def algorithm(fixed, student_list, elective_course_list ,group_course ,rounds=5):
    student_names = list(fixed[0].keys())
    ranks = list(fixed[0].values())
    for i in range(1, rounds + 1):
        print(i)
        round_data = ready_to_new_round(student_list, student_names, ranks)
        enroll_students(round_data, student_list, elective_course_list, group_course)
        second_phase(ranks, student_list, elective_course_list, i, group_course)



def order_course_data(raw_course_list):

    group_course_list = []
    course_list_elective_output = []
    course_list_mandatory_output = []
    possible_list = []
    max_office = 0
    for dic in raw_course_list:
        id_group = int(dic['id'])
        name = dic['name']
        office = int(dic['office'])
        if max_office < office:
            max_office = office

        elect = dic['is_elective']

        counter = 1
        for dic2 in dic['courses']:
            id = int(dic2['course_id'])
            semester = dic2['Semester']
            lecturer = dic2['lecturer']
            capacity = int(dic2['capacity'])
            day = dic2['day']
            start = dic2['time_start']
            end = dic2['time_end']
            tmp = Course(id, id_group, name + ' ' + str(counter), capacity, start, end, semester, day, lecturer, office, elect)
            counter += 1
            possible_list.append(tmp)

        if elect:
            for co in possible_list:
                course_list_elective_output.append(co)

        else:
            for co in possible_list:
                course_list_mandatory_output.append(co)

        new_group = Course_group(id_group, name, office, possible_list)
        group_course_list.append(new_group)
        possible_list.clear()

    return group_course_list, course_list_elective_output, course_list_mandatory_output, max_office


def overlap_course(course_list):
    for i in range(len(course_list)):
        overlap_list_for_i = []
        for j in range(len(course_list)):
            if not i == j:
                if course_list[j].get_day() == course_list[i].get_day():
                    if course_list[j].get_semester() == course_list[i].get_semester():
                        if course_list[j].get_start() <= course_list[i].get_start() < course_list[j].get_end():
                            overlap_list_for_i.append(course_list[j])

                        elif course_list[j].get_start() < course_list[i].get_end() <= course_list[j].get_end():
                            overlap_list_for_i.append(course_list[j])

                        elif course_list[j].get_start() == course_list[i].get_start() and \
                                course_list[i].get_end() == course_list[j].get_end():
                            overlap_list_for_i.append(course_list[j])

        course_list[i].set_overlap(overlap_list_for_i)
        overlap_list_for_i.clear()

def order_student_data(raw_student_list, raw_rank_list, elective_course_list, mandatory_course_list ,num_offices):
    indexed_enrollment = [{} for i in range(num_offices)]
    cardinal_order = [{} for i in range(num_offices)]
    student_list = [[] for i in range(num_offices)]
    course_list = [[] for i in range(num_offices)]

    for i in range(num_offices):
        course_list[i] = elective_course_list[i] + mandatory_course_list[i]


    for office_number in course_list:
        for i in office_number:
            indexed_enrollment[i.get_office()-1][i.get_name()] = 0

            if i.get_elective():
                cardinal_order[i.get_office()-1][i.get_name()] = 0


    for dic in raw_student_list:
        tmp1 = deepcopy(indexed_enrollment)
        tmp2 = deepcopy(cardinal_order)
        id = int(dic['student_id'])
        need_to_enroll = int(dic['amount_elective'])
        office = int(dic['office'])

        for i in range(len(course_list[office-1])):
            for dic2 in dic['courses']:
                if course_list[office-1][i].get_id() == int(dic2['course_id']):
                    tmp1[office-1][course_list[office-1][i].get_name()] = 1

        for rank_dic in raw_rank_list:
            student_id = int(rank_dic['student'][0:9])
            group_id = int(rank_dic['course_group'])
            rank = int(rank_dic['rank'])
            if student_id == id:
                for office_number in elective_course_list:
                    for course in office_number:
                        if course.get_id_group() == group_id:
                            tmp2[office-1][course.get_name()] = rank

        s = Student(id, need_to_enroll, office, deepcopy(tmp1[office-1]), deepcopy(tmp2[office-1]))
        student_list[office-1].append(s)


    return student_list


def sort_by_office_courses(course_list, num_offices):
    sort_office_list_course = [[] for i in range(num_offices)]

    for i in course_list:
        sort_office_list_course[i.get_office() - 1].append(i)


    return sort_office_list_course


def main(raw_student_list, raw_course_list, raw_rank_list):
    print(raw_student_list)
    print(raw_course_list)
    print(raw_rank_list)

    course_group_list, course_elect_list, course_mandatory_list, num_offices = order_course_data(raw_course_list)
    set_of_offices_elective_courses = sort_by_office_courses(course_elect_list, num_offices)
    set_of_offices_mandatory_courses = sort_by_office_courses(course_mandatory_list, num_offices)
    course_list = [[] for i in range(num_offices)]
    for index in range(num_offices):
        course_list[index] = set_of_offices_elective_courses[index] + set_of_offices_mandatory_courses[index]
        overlap_course(course_list[index])

    set_of_offices_students = order_student_data(raw_student_list, raw_rank_list, set_of_offices_elective_courses,
                                                 set_of_offices_mandatory_courses, num_offices)

    set_of_office_group = sort_by_office_courses(course_group_list, num_offices)


    fixed = []
    dic = {}
    for office_index in set_of_offices_students:
        for student in office_index:
            dic[student.get_id()] = student.get_cardinal()

        tmp = deepcopy(dic)
        fixed.append(tmp)

    for index in range(num_offices):
        algorithm(fixed, set_of_offices_students[index], set_of_offices_elective_courses[index], set_of_office_group[index])

    for office in set_of_offices_students:
        for i in office:
            i.to_string()
            print()

    for office in set_of_offices_elective_courses:
        for i in office:
            i.to_string()
            print()
    #row_number = len(ranking)
    #column_number = len(ranking[0])
    #fixed = create_matrix(ranking, courses, row_number, column_number)
    #student_list = create_students(fixed, courses)
    #course_list = create_courses(fixed)

    sum = 0
    for office_num in set_of_offices_students:
        for index in office_num:
            sum += index.get_number_of_enrollments()

    print(sum)

    '''
    row_number = len(ranking)
    column_number = len(ranking[0])
    fixed = create_matrix(ranking, courses, row_number, column_number)
    student_list = create_students(fixed, courses)
    course_list = create_courses(fixed)
    '''
