from Libs import *

# Zone Class
class Zone:
    def __init__(self, name, corners, mp, color = 'blue'):
        self.name = name
        self.corners = np.array(corners)
        self.visit = defaultdict(list)
        self.interaction = defaultdict(default_dict_list)
        self.color = color
        self.mp = mp
        self.ppl = {}
    
    def register_entry(self, person_id, entry_time):
        for person in self.ppl.values():
            person.start_interaction(self, person_id, entry_time)
        self.ppl[person_id] = self.mp.ppl[person_id]
        self.visit[person_id].append([entry_time, entry_time])

    def register_leave(self, person_id, leave_time):
        del self.ppl[person_id]
        for person in self.ppl.values():
            person.end_interaction(self, person_id, leave_time)
        self.visit[person_id][-1][1]=leave_time
        
    
    def start_interaction(self, person_ids, start_time):
        self.interaction[person_ids[0]][person_ids[1]].append([start_time, start_time])
        self.interaction[person_ids[1]][person_ids[0]].append([start_time, start_time])
    
    def end_interaction(self, person_ids, end_time):
        self.interaction[person_ids[0]][person_ids[1]][-1][1] = end_time
        self.interaction[person_ids[1]][person_ids[0]][-1][1] = end_time
    
    def pos_in_zone(self,pos):
        # Extract x and y values from corners
        x_values = self.corners[:, 0]
        y_values = self.corners[:, 1]

        # Determine the bounding box
        min_x = np.min(x_values)
        max_x = np.max(x_values)
        min_y = np.min(y_values)
        max_y = np.max(y_values)

        x_in_zone = pos[0]>=min_x and pos[0]<=max_x
        y_in_zone = pos[1]>=min_y and pos[1]<=max_y

        if x_in_zone and y_in_zone:
            return True
        else:
            return False

    def calculate_person_time(self, person_id):
        total = datetime.timedelta()
        for entry, leave in self.visit[person_id]:
            if leave:
                total += leave - entry
        return total*100

# Ppl Class
class Person:
    def __init__(self, person_id, pos, mp):
        self.person_id = person_id
        self.zone_log = defaultdict(list)  # {zone_name: [(entry_time, leave_time), ...]}
        self.interaction = defaultdict(default_dict_list)  # {zone_name: {person_id: (start_time, end_time)}}
        self.pos = np.array(pos)
        self.zone = mp.get_zone(pos)
        self.mp = mp

    def register_entry(self, zone, entry_time):
        zone.register_entry(self.person_id, entry_time)
        self.zone_log[zone.name].append([entry_time, entry_time])

    def register_leave(self, zone, leave_time):
        zone.register_leave(self.person_id, leave_time)
        self.zone_log[zone.name][-1][1] = leave_time

    def start_interaction(self, zone, person_id, start_time):
        zone.start_interaction((self.person_id, person_id), start_time)
        self.interaction[zone.name][person_id].append([start_time, start_time])
        self.mp.ppl[person_id].interaction[zone.name][self.person_id].append([start_time, start_time])
    
    def end_interaction(self, zone, person_id, end_time):
        zone.end_interaction((self.person_id, person_id), end_time)
        self.interaction[zone.name][person_id][-1][1] = end_time
        self.mp.ppl[person_id].interaction[zone.name][self.person_id][-1][1] = end_time

    def calculate_time_in_zone(self, zone_name):
        total = datetime.timedelta()
        for entrada, saida in self.zone_log[zone_name]:
            if saida:
                total += saida - entrada
        return total*100

    def random_move(self):
        self.pos += np.random.choice([-1,0,1])

# Map Control Class
class Map:
    def __init__(self, base_image_path, output_image_path, size_x, size_y, grid_size_x, grid_size_y):
        self.size_x = size_x
        self.size_y = size_y
        self.grid_size_x = grid_size_x
        self.grid_size_y = grid_size_y
        self.base_image_path = base_image_path
        self.output_image_path = output_image_path
        self.ppl = {}
        self.zones = {}
        self.hidden_zone = hz = Zone('hidden',None, self)
        self.image = create_blank_image(self.size_x,self.size_y)
        draw_grid(self.image, (self.grid_size_x, self.grid_size_y))
        self.image.save(self.base_image_path)

    def add_zone(self, zone):
        self.zones[zone.name] = zone
        paint_multi_cells(self.image, (self.grid_size_x, self.grid_size_y), zone.corners,color = zone.color)
        self.image.save(self.base_image_path)
    
    def add_person(self, person):
        self.ppl[person.person_id] = person
        person.register_entry(person.zone, datetime.datetime.now())
    
    def get_zone(self, pos):
        for zone in self.zones.values():
            if (zone.pos_in_zone(pos)):
                return zone
        return self.hidden_zone

    def update_positions(self):
        hora_atual = datetime.datetime.now()

        image = Image.open(self.base_image_path)
        draw = ImageDraw.Draw(image)

        # Adicionar novos pontos vermelhos
        for person in self.ppl.values():
            x_center = person.pos[0] * self.grid_size_x + self.grid_size_x // 2
            y_center = person.pos[1] * self.grid_size_y + self.grid_size_y // 2
            radius = min(self.grid_size_x, self.grid_size_y) // 4  # Ajustar tamanho conforme necessário
            draw.ellipse((x_center - radius, y_center - radius, x_center + radius, y_center + radius), fill='red') # Ajustar para token

        
        # Salvar a imagem modificada
        image.save(self.output_image_path)

        for person in self.ppl.values():
            # Encontrar a zona atual da pessoa antes de mover
            old_zone = person.zone
            new_zone = self.get_zone(person.pos)

            # Registrar saída da zona atual
            if old_zone.name != new_zone.name:
                person.register_entry(new_zone, hora_atual)
                if person.zone is not None:
                    person.register_leave(old_zone, hora_atual)

            person.zone = new_zone

    def save_state(self, filename):
        with open(filename, 'wb') as file:
            pickle.dump(self, file)

    @staticmethod
    def load_state(filename):
        with open(filename, 'rb') as file:
            return pickle.load(file)

# User Interface Class
class MapInterface:
    def __init__(self, root, map_filename):
        self.root = root
        self.root.title("Map Interface")
        
        self.load_map(map_filename)
        
        self.create_widgets()
        
    def load_map(self, filename):
        with open(filename, 'rb') as file:
            self.map_data = pickle.load(file)
    
    def create_widgets(self):
        self.zone_listbox = tk.Listbox(self.root)
        self.zone_listbox.grid(row=0, column=0, padx=10, pady=10)
        
        for zone_name in self.map_data.zones.keys():
            self.zone_listbox.insert(tk.END, zone_name)
        
        self.view_zone_button = tk.Button(self.root, text="View Zone Info", command=self.view_zone_info)
        self.view_zone_button.grid(row=1, column=0, padx=10, pady=10)
        
        self.person_listbox = tk.Listbox(self.root)
        self.person_listbox.grid(row=0, column=1, padx=10, pady=10)
        
        for person_id in self.map_data.ppl.keys():
            self.person_listbox.insert(tk.END, person_id)
        
        self.view_person_button = tk.Button(self.root, text="View Person Info", command=self.view_person_info)
        self.view_person_button.grid(row=1, column=1, padx=10, pady=10)
        
        self.info_text = tk.Text(self.root, wrap='word', width=50, height=20)
        self.info_text.grid(row=0, column=2, rowspan=2, padx=10, pady=10)
    
    def view_zone_info(self):
        selected_zone = self.zone_listbox.get(tk.ACTIVE)
        if selected_zone:
            zone = self.map_data.zones[selected_zone]
            info = f"Zone Name: {zone.name}\n\n"
            info += "Visits:\n"
            for person_id, times in zone.visit.items():
                info += f"  Person {person_id}:\n"
                for entry, leave in times:
                    info += f"    Entry: {entry}, Leave: {leave}\n"
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(tk.END, info)
        else:
            messagebox.showwarning("No Selection", "Please select a zone to view information.")
    
    def view_person_info(self):
        selected_person_id = self.person_listbox.get(tk.ACTIVE)
        if selected_person_id is not None:
            person = self.map_data.ppl[int(selected_person_id)]
            info = f"Person ID: {person.person_id}\n\n"
            info += f"Position: {person.pos}\n"
            info += f"Current Zone: {person.zone.name}\n\n"
            info += "Time in Zones:\n"
            for zone_name, times in person.zone_log.items():
                total_time = datetime.timedelta()
                for entry, leave in times:
                    if leave:
                        total_time += leave - entry
                info += f"  Zone {zone_name}: {total_time}\n"
            info += "\nInteractions:\n"
            for zone_name, interactions in person.interaction.items():
                info += f"  Zone {zone_name}:\n"
                for other_person_id, times in interactions.items():
                    info += f"    With Person {other_person_id}:\n"
                    for start, end in times:
                        info += f"      Start: {start}, End: {end}\n"
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(tk.END, info)
        else:
            messagebox.showwarning("No Selection", "Please select a person to view information.")


