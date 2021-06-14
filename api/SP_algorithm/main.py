from copy import deepcopy, copy
import logging
from api.SP_algorithm.course import OOPCourse
from api.SP_algorithm.course_group import Course_group
from api.SP_algorithm.student import OOPStudent
from api.models import Result, Course, Student


#logging.basicConfig(level=logging.DEBUG)


def check_overlap(student_object, course_object): # Check if there is an overlap course to the course we tried to enroll
    overlap_courses = course_object.get_overlap_list()
    if len(overlap_courses) > 0:  # If there isn't overlap course we can simply say there isn't an overlap course
        output = True   # We'll presume there is no enrolled course such that is overlapped with course_object
        enroll_status = student_object.get_enrolment_status()
        logging.info("Checking if there is overlap course to course_object such that student_object try to enroll")
        for overlap in range(len(overlap_courses)):
            course_name = overlap_courses[overlap]
            check = enroll_status[course_name.get_name()]
            if check == 1:  # If The student is enroll to overlap course
                student_object.delete_current_preference()
                if output:
                    output = False
                    break

        return output

    else:
        return True


def there_is_a_tie(students_object):
    logging.info("We trying to enrolling more students to a course such that the number of student exceed"
                 "the remaining capacity")

    # We create a list of 0 with the length of the number of students that in this round want to enroll
    # and than we change the number zero where there is a tie between the bids when if there is several bids
    # the highest tie we change the index location to 1 (in the zeroes list) find another tie but smaller we change
    # 0 into 2 and so on this list helps us to sort afterward the students according to their bids if there is a tie
    start_end = [0 for i in range(len(students_object))]
    counter = 1
    for index in range(len(students_object) - 1):
        if students_object[index].get_current_highest_bid() == students_object[index + 1].get_current_highest_bid():
            start_end[index] = counter
            start_end[index + 1] = counter

        elif students_object[index].get_current_highest_bid() != students_object[index + 1].get_current_highest_bid() \
                and start_end[index] != 0:
            counter += 1

    return start_end


def sort_tie_breaker(student_object_try, check, course_name):
    logging.info(
        "There is a tie between some students so we sort the tie breaker between all the tie in the current list")
    max_value = max(check)
    for i in range(1, max_value + 1):
        min_index = check.index(i)
        max_index = len(check) - check[::-1].index(i) - 1  # sort other way around and find the index of the element i
        # for getting the last appearance of the i tie when 1 is the highest tie and max_value is the smallest tie
        tie_student = student_object_try[min_index:max_index]
        # Take a sub list to activate on this sub list the sort function
        fixed_tie_student = sorted(tie_student, key=lambda x: (
            x.get_number_of_enrollments(), x.current_highest_ordinal(course_name)), reverse=False)
        student_object_try[min_index:max_index] = fixed_tie_student
        # Insert back the sorted sub list into the list that
        # indicate about the ties in the same places


def new_enroll_students(student_list, elective_course_list, round):
    student_need_to_enroll = copy(student_list)
    while len(student_need_to_enroll) > 0:
        student_need_to_enroll = list(filter(lambda x: x.get_number_of_enrollments() < round, student_need_to_enroll))
        student_need_to_enroll = list(filter(lambda x: x.get_current_highest_bid() != 0, student_need_to_enroll))
        student_need_to_enroll = sorted(student_need_to_enroll, key=lambda x: x.get_current_highest_bid(), reverse=True)
        need_to_break = False
        for student in student_need_to_enroll:
            try_to_enroll = student.get_next_preference()
            tmp_preference = list(try_to_enroll.items())
            course_name = tmp_preference[0]
            for course in elective_course_list:
                if course.get_name() == course_name[0]:
                    if check_overlap(student, course):
                        if student.get_need_to_enroll() > 0 and course.get_capacity()>0:
                            course.student_enrollment(student.get_id(),student)
                            student.got_enrolled(course.get_name())
                            s = Student.objects.get(student_id=student.get_id())
                            c = Course.objects.get(course_id=course.get_id())
                            Result.objects.create(course=c, student=s, selected=True)


                        else:
                            student.add_gap(True, course_name[1])
                            need_to_break = True
                            break

                    else:
                        student.add_gap(False)
                        need_to_break = True
                        break

            if need_to_break:
                break


def algorithm(student_list, elective_course_list, rounds=5):
    for i in range(1, rounds + 1):
        logging.info("Starting round number %d", i)
        new_enroll_students(student_list, elective_course_list, i)


# Changes the orderDic of courses that we getting from the server and convert to an object OOPCourse
def order_course_data(raw_course_list):
    logging.info(
        "Create the course list that will contain the course data that "
        "the program get from the server about courses and group courses")

    group_course_list = []
    course_list_elective_output = []
    course_list_mandatory_output = []
    possible_list = []

    logging.info("Starting the procedure of convert order dictionary we got from the server to group course")
    create_course = 0
    create_group = 0

    for dic in raw_course_list:
        id_group = int(dic['id'])
        name = dic['name']
        id_office = int(dic['office'])
        elect = dic['is_elective']

        counter = 1
        for dic2 in dic['courses']: # dic2 is representing the courses of group_course (= dic1)
            id = int(dic2['course_id'])
            semester = dic2['Semester']
            lecturer = dic2['lecturer']
            capacity = int(dic2['capacity'])
            day = dic2['day']
            start = dic2['time_start']
            end = dic2['time_end']
            tmp = OOPCourse(id, id_group, name + ' ' + str(counter), capacity, start, end, semester, day, lecturer,
                            id_office, elect)
            logging.info("Finish the procedure of create a new course number %d", create_course)
            create_course += 1
            counter += 1
            possible_list.append(tmp)

        if elect:
            for co in possible_list:
                course_list_elective_output.append(co)

        else:
            for co in possible_list:
                course_list_mandatory_output.append(co)

        new_group = Course_group(id_group, name, id_office, copy(possible_list))
        logging.info("Finish the procedure of create a new group course number %d and named %s", create_group, name)
        create_group += 1
        group_course_list.append(new_group)
        possible_list.clear()

    return group_course_list, course_list_elective_output, course_list_mandatory_output


def overlap_course(course_list):
    # Check which course is overlap each and other, for overlap the courses must be
    # in the same semester and day before checking if they overlap.
    # Afterward we check if course is starting while other course has been starting and finish later or
    # the course is ending while other course has been start and not finish yet or the starting and ending
    # time is the same. this is the three option that if one of that happened we add the other course
    # to the list of overlap courses the course we checking currently

    for i in range(len(course_list)):
        overlap_list_for_i = []
        for j in range(len(course_list)):
            if not i == j:  # If it's not same course
                if course_list[j].get_day() == course_list[i].get_day():  # If it's in the same day
                    if course_list[j].get_semester() == course_list[i].get_semester():  # If it's in the same day
                        if course_list[j].get_start() <= course_list[i].get_start() < course_list[j].get_end():
                            overlap_list_for_i.append(course_list[j])

                        elif course_list[j].get_start() < course_list[i].get_end() <= course_list[j].get_end():
                            overlap_list_for_i.append(course_list[j])

                        elif course_list[j].get_start() == course_list[i].get_start() and \
                                course_list[i].get_end() == course_list[j].get_end():
                            overlap_list_for_i.append(course_list[j])

        course_list[i].set_overlap(overlap_list_for_i)
        overlap_list_for_i.clear()


def order_student_data(raw_student_list, raw_rank_list, elective_course_list, course_list):
    counter = 0
    logging.info(
        "create the student list that will contain the data such that the program get from the server about students")
    indexed_enrollment = {}
    cardinal_order = {}
    student_list = []

    for i in course_list:
        indexed_enrollment[i.get_name()] = 0

        if i.get_elective():
            cardinal_order[i.get_name()] = 0

    logging.info("starting the procedure of convert order dictionary we got from the server to students")

    for dic in raw_student_list:
        deepcopy_indexed_enrollment = deepcopy(indexed_enrollment)
        deepcopy_cardinal_order = deepcopy(cardinal_order)
        id = int(dic['student_id'])
        need_to_enroll = int(dic['amount_elective'])
        office = int(dic['office'])

        # Updating the enrollment status for mandatory courses

        for i in range(len(course_list)):
            for dic2 in dic['courses']:
                if course_list[i].get_id() == int(dic2['course_id']):
                    deepcopy_indexed_enrollment[course_list[i].get_name()] = 1

        for rank_dic in raw_rank_list:  # Update the ranking of elective courses for all student in current office
            student_id = int(rank_dic['student'][0:9]) # Taking the student id for checking if is the same student
            course_id = int(rank_dic['course'])
            rank = int(rank_dic['rank'])
            #if rank == 0:
            #    rank += 1

            if student_id == id:
                for course in elective_course_list:
                    if course.get_id() == course_id:
                        deepcopy_cardinal_order[course.get_name()] = rank

        logging.info(
            "Create a new student number %d and insert him to the student_list in the row of his office number %d",
            counter, office)

        s = OOPStudent(id, need_to_enroll, office, deepcopy(deepcopy_indexed_enrollment), deepcopy(deepcopy_cardinal_order))
        student_list.append(s)
        counter += 1

    return student_list


def main(raw_student_list, raw_course_list, raw_rank_list):
    print(raw_student_list)
    print(raw_course_list)
    print(raw_rank_list)

    course_group_list, course_elect_list, course_mandatory_list = order_course_data(raw_course_list)
    # logging.info("Sorting the elective courses into office according to the number of offices")
    # set_of_offices_elective_courses = sort_by_office_courses(course_elect_list, num_offices)
    # logging.info("Sorting the mandatory courses into office according to the number of offices")
    # set_of_offices_mandatory_courses = sort_by_office_courses(course_mandatory_list, num_offices)

    logging.info("Now merging the elective and mandatory courses for checking possible overlap while maintaining the"
                 "separation of courses according to the office number")

    course_list = course_elect_list + course_mandatory_list
    overlap_course(course_list)

    logging.info(
        "while convert the student data from order dictionary to Student we sort student according to their office ")
    student_list = order_student_data(raw_student_list, raw_rank_list, course_elect_list, course_list)

    logging.info("Order the data for the algorithm in a list of dictionaries as each dictionary is represent"
                 " a single office while the data is portrayed by {student id: dictionary of cardinal ranking"
                 " of the same student}")
    fixed = {}
    for student in student_list:
        fixed[student.get_id()] = student.get_cardinal()

    logging.info("Activate the algorithm")
    algorithm(student_list, course_elect_list)

    for i in student_list:
        i.to_string()
        print()

    for i in course_elect_list:
        i.to_string()
        print()

    sum = 0
    for i in student_list:
        sum += i.get_number_of_enrollments()
    print(sum)