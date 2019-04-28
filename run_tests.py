import os
import sys

SAVE_LOG_DETAILS = True
SHOW_PLOTS = False
ROOT_DIR = "../../test_output"
PYTHON_COMMAND = 'python'

def select_test_and_run():
    #main()
    #main_test()
    #short_test()
    final_test_1(sys.argv[1:])
    #final_test_2(sys.argv[1:])

def final_test_2(argv_indexes):
    indexes = [int(i) for i in argv_indexes]
    print(indexes)
    if not os.path.exists(ROOT_DIR): os.makedirs(ROOT_DIR)

    import time
    start_time = time.time()
    test_count = 0
    for runIndex in indexes:
        for numUser in [20]:
            for numTimeSlot in [86400]:
                for numRepeats in [60]:
                    instances_to_test = [
                        'instance_f1',
                        'instance_cont_f1',
                    ]

                    for problemInstance in instances_to_test:
                        for periodOption in [20]:
                            test_count += 1
                            run_with_args(
                                algorithmName="EXP4",
                                numRepeats=numRepeats,
                                periodOption=periodOption,
                                gammaOption=5,
                                numMobileUser=numUser,
                                problemInstance=problemInstance,
                                numTimeSlot=numTimeSlot,
                                runIndex=runIndex,
                            )
                            curr_time = int(time.time() - start_time)
                            print('---------------------')
                            print('TEST %d DONE - Index=%d, Prob=%s, Per=%d' % 
                                (test_count, runIndex, problemInstance, periodOption))
                            print('Time Elapsed: %d minutes %d seconds' % (curr_time//60, curr_time%60))
                            print('---------------------')

def final_test_1(argv_indexes):
    indexes = [int(i) for i in argv_indexes]
    print(indexes)
    if not os.path.exists(ROOT_DIR): os.makedirs(ROOT_DIR)

    import time
    start_time = time.time()
    test_count = 0
    for runIndex in indexes:
        for numUser in [20]:
            for numTimeSlot in [86400]:#[86400]:
                for numRepeats in [60]:#[60]:
                    instances_to_test = [
                        'instance_f1',
                        'instance_cont_f1',
                        #'instance_cont_f2',
                    ]

                    for problemInstance in instances_to_test:
                        for periodOption in [0,20]:#,14,15,20,17]:
                            test_count += 1
                            run_with_args(
                                algorithmName="EXP4",
                                numRepeats=numRepeats,
                                periodOption=periodOption,
                                gammaOption=5,
                                numMobileUser=numUser,
                                problemInstance=problemInstance,
                                numTimeSlot=numTimeSlot,
                                runIndex=runIndex,
                            )
                            curr_time = int(time.time() - start_time)
                            print('---------------------')
                            print('TEST %d DONE - Index=%d, Prob=%s, Per=%d' % 
                                (test_count, runIndex, problemInstance, periodOption))
                            print('Time Elapsed: %d minutes %d seconds' % (curr_time//60, curr_time%60))
                            print('---------------------')

def short_test():
    if not os.path.exists(ROOT_DIR): os.makedirs(ROOT_DIR)

    for numUser in [6,12]:
        for numTimeSlot in [60000]:
            for numRepeats in [5]:
                instances_to_test = [
                    'instance_cont1',
                    'instance_cont3',
                ]
                for problemInstance in instances_to_test:
                    for periodOption in [0,5,6,8,12]:
                        run_with_args(
                            algorithmName="EXP4",
                            numRepeats=numRepeats,
                            periodOption=periodOption,
                            gammaOption=1,
                            numMobileUser=numUser,
                            problemInstance=problemInstance,
                            numTimeSlot=numTimeSlot,
                            runIndex=1,
                        )

def main():
    if not os.path.exists(ROOT_DIR): os.makedirs(ROOT_DIR)

    for numUser in [6,12]:
        for numTimeSlot in [480,960,2400,12000,24000]:
            for numRepeats in [10,30]:
                instances_to_test = [
                    'instance_cont1',
                    'instance_cont2',
                    'instance_cont3',
                    #'instance_cont6',
                    'instance_2', # cycle 5
                    'instance_3', # cycle 5, extreme binary case
                    'instance_4', # cycle 7
                ]

                for problemInstance in instances_to_test:
                    for periodOption in [0,1,3,5]:
                        run_with_args(
                            algorithmName="EXP4",
                            numRepeats=numRepeats,
                            periodOption=periodOption,
                            gammaOption=1,
                            numMobileUser=numUser,
                            problemInstance=problemInstance,
                            numTimeSlot=numTimeSlot,
                            runIndex=1,
                        )

def main_test():
    if not os.path.exists(ROOT_DIR): os.makedirs(ROOT_DIR)

    for numUser in [6]:
        for numTimeSlot in [120000]:
            for numRepeats in [100]:
                instances_to_test = [
                    'instance_cont1',
                    'instance_cont2',
                    'instance_cont3',
                    'instance_4',
                ]

                for problemInstance in instances_to_test:
                    for periodOption in [x+13 for x in range(1,41)]:#[0,5,6,7,8,9,10]:
                        run_with_args(
                            algorithmName="EXP4",
                            numRepeats=numRepeats,
                            periodOption=periodOption,
                            gammaOption=1,
                            numMobileUser=numUser,
                            problemInstance=problemInstance,
                            numTimeSlot=numTimeSlot,
                            runIndex=1,
                        )


def format_arg(v):
    if type(v) == str: return '"%s"' % v
    return str(v)

def format(args):
    return ' '.join('-%s %s' % (k, format_arg(v)) for k,v in args)

def generate_dir_name(args):
    tuples = list(args)
    tuples.sort(key=lambda x:x[0])
    return '--'.join('%s_%s' % (key, str(value).replace(' ','_')) for key, value in tuples)

def run_with_args (
        algorithmName,
        numRepeats,
        periodOption,
        gammaOption,
        numMobileUser,
        problemInstance,
        numTimeSlot,
        runIndex,
    ):
    args = [
        ('a', algorithmName),
        ('rep', numRepeats),
        ('per', periodOption),
        ('gam', gammaOption),
        ('n', numMobileUser),
        ('p', problemInstance),
        ('t', numTimeSlot),
        ('r', runIndex),
    ]
    dirName = '%s/%s' % (ROOT_DIR, generate_dir_name(args))
    args += [
        ('dir', dirName),
        ('log', SAVE_LOG_DETAILS),
        ('plot', SHOW_PLOTS),
    ]

    cmd = '%s wns.py %s' % (PYTHON_COMMAND, format(args))

    #print(cmd)
    print('RUN: %s' % cmd)
    os.system(cmd)


if __name__ == '__main__':
    select_test_and_run()