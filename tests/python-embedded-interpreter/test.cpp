#include <stdio.h>
#include <vector>
int
main ()
{
  std::vector<int> v (1, 2);
  std::vector<int>::iterator it(v.begin());
  return 0;
}
