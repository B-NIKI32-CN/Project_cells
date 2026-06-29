# После окончания боезапаса (0) при выстреле высвечивается 1, в следующем ходу боезапас 0

# Рядом со стеной пуля может не вылететь из танка

# Вылет с ошибкой после уничтожения базы 
Traceback (most recent call last):
  File "<frozen runpy>", line 198, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "/home/starodub/Documents/Projects/Project_cells/src/main.py", line 302, in <module>
    cur_player.mist_matrix = utils.functions.mist_doting3000(cur_player.tanks, cur_player.base,
                             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/starodub/Documents/Projects/Project_cells/src/utils/functions.py", line 108, in mist_doting3000
    A[base.sprites()[0].place[1], base.sprites()[0].place[0]] = 1
      ~~~~~~~~~~~~~~^^^
IndexError: list index out of range