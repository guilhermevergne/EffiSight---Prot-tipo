from Classes import *

# Example usage
image_path = 'Map.png'
output_image_path = 'Map_sim.png'
image_size_x = 500
image_size_y = 500
grid_size_x,grid_size_y = (50,50)
zones = []
zones.append(np.array([(0, 0), (0, 3), (3, 0), (3, 3)]))
zones.append(np.array([(6, 0), (6, 3), (9, 0), (9, 3)]))
zones.append(np.array([(0, 6), (0, 9), (3, 6), (3, 9)]))
zones.append(np.array([(6, 6), (6, 9), (9, 6), (9, 9)]))
mp = Map(image_path,output_image_path,image_size_x,image_size_y,grid_size_x,grid_size_y)
mp.add_zone(Zone('A',zones[0], mp))
mp.add_zone(Zone('B',zones[1], mp))
mp.add_zone(Zone('C',zones[2], mp))
mp.add_zone(Zone('D',zones[3], mp))

mp.add_person(Person(0,[4,5],mp))
mp.add_person(Person(1,[4,5],mp))
mp.add_person(Person(2,[6,7],mp))
mp.add_person(Person(3,[6,7],mp))



for i in range(1000):
    for person in mp.ppl.values():
        person.random_move()
    mp.update_positions()

for person in mp.ppl.values():
    print(f'\n\n{person.person_id}')
    print(f'{mp.hidden_zone.name}: {person.calculate_time_in_zone(mp.hidden_zone.name)}')
    for zone in mp.zones.values():
        print(f'{zone.name}: {person.calculate_time_in_zone(zone.name)}')

# Salvar o estado do mapa
mp.save_state('map_state.pkl')

# Carregar o estado do mapa
mp_loaded = Map.load_state('map_state.pkl')

# Verificar se o estado carregado é o mesmo que foi salvo
for person in mp_loaded.ppl.values():
    print(f'\n\n{person.person_id}')
    print(f'{mp_loaded.hidden_zone.name}: {person.calculate_time_in_zone(mp_loaded.hidden_zone.name)}')
    for zone in mp_loaded.zones.values():
        print(f'{zone.name}: {person.calculate_time_in_zone(zone.name)}')