g++ -std=c++11 -o3 -c -fPIC periodicexp4.cpp -o periodicexp4.o
g++ -shared -Wl,-soname,libperiodicexp4.so -o libperiodicexp4.so  periodicexp4.o