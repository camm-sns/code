#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <math.h>
using namespace std;

int main (int argc, char *argv[]) {
  string parname;
  int n;
  double p0,chisq;
  vector<double> par;
  ifstream myfile (argv[1]);
  if (myfile.is_open())
  {
    myfile >> n >> parname;
    for (int i=0; i<n; i++)
    {
      myfile >> p0 >> parname;
      par.push_back(p0);
    }
    myfile.close();
  }
  else cout << "Unable to open file"; 
  chisq = 0.0;
  for (int i=0; i<n; i++)
  {
    chisq += pow(par[i]-double(i+1),2);
  }
  ofstream outfile;
  outfile.open(argv[2]);
  outfile << chisq<<" obj_fn\n";
  outfile.close();

  return 0;
}
