saveLogDetails=true
showPlots=false
numMobileUser=20
problemInstance="instance_cont_f1"
numRun=1
numTimeSlot=1200
algorithmName="EXP4"
numRepeats=40
periodOption=20
gammaOption=5
rootDir="../../test_output"
pythonCommand=python

mkdir $rootDir

runIndex=1
while [  $runIndex -lt $((numRun+1)) ]; do
    dir="$rootDir/run_vgtest2_$runIndex/"
    mkdir $dir
    $pythonCommand wns.py -rep $numRepeats -per $periodOption -gam $gammaOption -log $saveLogDetails -n $numMobileUser -p $problemInstance -t $numTimeSlot -a $algorithmName -dir "$dir" -r $runIndex -plot $showPlots
    runIndex=$((runIndex + 1 ))
done