import os

SAVE_LOG_DETAILS = True
SHOW_PLOTS = False
ROOT_DIR = "../../test_output"
PYTHON_COMMAND = 'python'

def main():
    if not os.path.exists(ROOT_DIR): os.makedirs(ROOT_DIR)

    for numUser in [6,12]:
        for numTimeSlot in [480,960,2400,12000,24000]:
            for numRepeats in [1,2,3,5,10,30]:
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
                            numMobileUser=numUser,
                            problemInstance=problemInstance,
                            numTimeSlot=numTimeSlot,
                            runIndex=1,
                        )

def main_test():
    if not os.path.exists(ROOT_DIR): os.makedirs(ROOT_DIR)

    for numUser in [6]:
        for numTimeSlot in [12000]:
            for numRepeats in [10]:
                instances_to_test = [
                    'instance_cont1',
                    'instance_cont2',
                    'instance_cont3',
                ]

                for problemInstance in instances_to_test:
                    for periodOption in [x+13 for x in range(41)]:#[0,5,6,7,8,9,10]:
                        run_with_args(
                            algorithmName="EXP4",
                            numRepeats=numRepeats,
                            periodOption=periodOption,
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
        numMobileUser,
        problemInstance,
        numTimeSlot,
        runIndex,
    ):
    args = [
        ('a', algorithmName),
        ('rep', numRepeats),
        ('per', periodOption),
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
    #main()
    main_test()