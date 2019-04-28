saveLogDetails=true
showPlots=false
numMobileUser=20
problemInstance="mobility_setup3"
numRun=1
numTimeSlot=48
algorithmName="EXP4"
numRepeats=1
periodOption=13
gamma=-0.1
optimization=False
: '
problemInstance="continuous"
negative value for gamma implies that a time-varying gamma (defined in algo_periodicexp4.py) will be used
numTimeSlot=86400 - 60 repetitions of 1440 - selection done once every minute
rootDir="../simulationResults/EXP4_without_approximation"
'
rootDir="../simulationResults/test"
pythonCommand=python3

mkdir $rootDir

runIndex=1
while [  $runIndex -lt $((numRun+1)) ]; do
    dir="$rootDir/run$runIndex/"
    mkdir $dir
    $pythonCommand wns.py -rep $numRepeats -per $periodOption -log $saveLogDetails -n $numMobileUser -p $problemInstance -t $numTimeSlot -a $algorithmName -dir "$dir" -r $runIndex -plot $showPlots -gamma $gamma -o $optimization
    runIndex=$((runIndex + 1 ))
done
$pythonCommand combineRunResults.py -dir $rootDir/ -n $numRun -p $problemInstance
: '
assuming duration of a time slot = 15 seconds, 1 day => 5760 time slots
15 days - 86400
'