#include <chrono>
#include <ctime>
#include <string>
#include <iostream>



std::string asString (const std::chrono::high_resolution_clock::time_point& tp)
{
     // convert to system time:
     std::time_t t = std::chrono::high_resolution_clock::to_time_t(tp);
     std::string ts = std::ctime(&t);// convert to calendar time
     ts.resize(ts.size()-1);         // skip trailing newline
     return ts;
}

int main()
{
 
     // print the epoch of this system clock:
     std::chrono::high_resolution_clock::time_point tp;
     std::cout << "epoch: " << asString(tp) << std::endl;

     
     // print current time:
     tp = std::chrono::high_resolution_clock::now();
     std::cout << "now:   " << asString(tp) << std::endl;

     std::cout << "seconds since epoch " << std::chrono::duration_cast<std::chrono::seconds>(tp.time_since_epoch()).count() << "\n";


     // print minimum time of this system clock:
     tp = std::chrono::high_resolution_clock::time_point::min();
     std::cout << "min:   " << asString(tp) << std::endl;

     // print maximum time of this system clock:
     tp = std::chrono::high_resolution_clock::time_point::max();
     std::cout << "max:   " << asString(tp) << std::endl;

     
}

