# Energy Management Decision Algorithm

Run main.py

Args:

- -ev, type=int, default = 2, help="number of Evs"
- -batt, type=int, default = 1, help="number of Stationary Batteries"
- -alg, type=str, default="smart", choices=["smart", "base"], help="Decision algorithm"
- -house, type=int, default = 0, help="Test File"
- -pA, type=int, default = 10, help="Panel Area"
- -pF, type=str, default="London", choices=["Portugal", "London"], help="Production file"
- -grid, type=str, default="dynamic", choices=["flat", "dynamic"], help="Grid Price"
- --cheat, help="Read consumption prediction in cheat file (faster)"

example: \
$ python3 main.py -ev 3 -house 1 --cheat