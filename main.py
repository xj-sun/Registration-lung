

from registrationMethod import Registration


if __name__ == '__main__':

        Registration().registration_1()
        Registration().registration_2()
        #Registration().registration_3() # only for 2D
        Registration().registration_4()
        Registration().registrationBSpline_1()
        Registration().registrationBSpline_2()
        Registration().registrationBSpline_3()
        Registration().registrationDisplacement()
        Registration().registrationExhaustive()



        #all_txt_files = list(filter(lambda x: x.endswith('.txt'), os.listdir(the_dir)))