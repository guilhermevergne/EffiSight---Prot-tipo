import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw
import datetime
from collections import defaultdict
import pickle
import tkinter as tk
from tkinter import ttk, messagebox

#############################################################################################################
#                                                                                                           #
#                                                                                                           #
#                                               Map Creation                                                #
#                                                                                                           #
#                                                                                                           #
#############################################################################################################

def create_blank_image(image_size_x, image_size_y):
    # Create a blank white image
    image = Image.new('RGB', (image_size_x, image_size_y), 'white')
    return image

def draw_grid(image, grid_size):
    draw = ImageDraw.Draw(image)
    image_size_x, image_size_y = image.size

    # Draw grid lines
    for i in range(0, image_size_x, grid_size[0]):
        draw.line([(i, 0), (i, image_size_y)], fill='black', width=1)
    for j in range(0, image_size_y, grid_size[1]):
        draw.line([(0, j), (image_size_x, j)], fill='black', width=1)

def paint_cells(image, grid_size, coordinates, color='blue'):
    draw = ImageDraw.Draw(image)
    for coord in coordinates:
        x0 = coord[0] * grid_size[0]
        y0 = coord[1] * grid_size[1]
        x1 = x0 + grid_size[0]
        y1 = y0 + grid_size[1]
        draw.rectangle([x0, y0, x1, y1], fill=color)
    draw_grid(image, grid_size)

def gen_internal_coordinates(corners):
    # Convert corners to numpy array if it's not already
    corners = np.array(corners)

    # Extract x and y values from corners
    x_values = corners[:, 0]
    y_values = corners[:, 1]

    # Determine the bounding box
    min_x = np.min(x_values)
    max_x = np.max(x_values)
    min_y = np.min(y_values)
    max_y = np.max(y_values)

    # Generate internal coordinates
    #internal_coordinates = [(x, y) for x in range(min_x, max_x + 1) for y in range(min_y, max_y + 1)]

    # Generate internal coordinates using numpy
    x_range = np.arange(min_x, max_x + 1)
    y_range = np.arange(min_y, max_y + 1)
    xv, yv = np.meshgrid(x_range, y_range)
    internal_coordinates = np.column_stack([xv.ravel(), yv.ravel()])

    return internal_coordinates


def paint_multi_cells(image, grid_size, matrix, color='blue'):
    coordinates = gen_internal_coordinates(matrix)
    paint_cells(image, grid_size, coordinates, color)

def im_show(image):
    # Display the image using matplotlib
    plt.imshow(image)
    plt.show()

def default_dict_list():
    return defaultdict(list)

#############################################################################################################
#                                                                                                           #
#                                                                                                           #
#                                                 Map Moves                                                 #
#                                                                                                           #
#                                                                                                           #
#############################################################################################################

def update_positions(base_image_path, output_image_path, grid_size, new_positions):
    # Carregar a imagem base
    image = Image.open(base_image_path)
    draw = ImageDraw.Draw(image)

    # Adicionar novos pontos vermelhos
    for pos in new_positions:
        x_center = pos[0] * grid_size[0] + grid_size[0] // 2
        y_center = pos[1] * grid_size[1] + grid_size[1] // 2
        radius = min(grid_size[0], grid_size[1]) // 4  # Ajustar tamanho conforme necessário
        draw.ellipse((x_center - radius, y_center - radius, x_center + radius, y_center + radius), fill='red')

    # Exibir a imagem
    image.show()

    # Salvar a imagem modificada
    image.save(output_image_path)

def pos_in_zone(zones,pos):
    for zone, corners in enumerate(zones):
        # Convert corners to numpy array if it's not already
        corners = np.array(corners)
        # Extract x and y values from corners
        x_values = corners[:, 0]
        y_values = corners[:, 1]

        # Determine the bounding box
        min_x = np.min(x_values)
        max_x = np.max(x_values)
        min_y = np.min(y_values)
        max_y = np.max(y_values)

        x_in_zone = pos[0]>=min_x and pos[0]<=max_x
        y_in_zone = pos[1]>=min_y and pos[1]<=max_y
        if x_in_zone and y_in_zone:
            return zone+1
    return 0

def random_move(pos_old):
    positions_array = np.array(pos_old)

    # Atualizar posições
    new_x = positions_array[:, 0] + np.random.choice([-1,0,1])
    new_y = positions_array[:, 1] + np.random.choice([-1,0,1])
    ids = positions_array[:, 2]

    # Combinar as novas coordenadas com os ids
    new_positions_array = np.column_stack((new_x, new_y, ids))

    return new_positions_array

