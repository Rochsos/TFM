import instaloader
import random
import time
import os
import pickle
from datetime import datetime
from instaloader.exceptions import ConnectionException, ProfileNotExistsException

class MyRateController(instaloader.RateController):
    def sleep(self, secs):
        wait_time=random.uniform(60, 110)
        print(f"Durmiendo durante {wait_time} segundos")
        time.sleep(wait_time)

    def count_per_sliding_window(self, query_type):
        return 20

L = instaloader.Instaloader(rate_controller=lambda ctx: MyRateController(ctx))

# Cargar la sesión o iniciar sesión
try:
    L.load_session_from_file('unirtfminfluencer')
except:
    L.login('*******', '*******')
    L.save_session_to_file('unirtfminfluencer')


# Cargar influencers, si existe el archivo
try:
    with open('influencers.pkl', 'rb') as f:
        influencers = pickle.load(f)
except FileNotFoundError:
    with open("fitness_nutricion_influencers.txt", "r") as file:
        influencers = file.read().split(',')


# Cargar post_indexes, si existe
try:
    with open('post_indexes.pkl', 'rb') as f:
        post_indexes = pickle.load(f)
except FileNotFoundError:
    post_indexes = {}


total_downloads = 0
max_downloads_per_influencer = 250
max_downloads_total = 140

influencer_posts_downloaded = {}

while influencers:
    for influencer in influencers[:]:
        name, type = influencer.split(':')
        influencer_downloads = influencer_posts_downloaded.get(name, 0)
        post_index = post_indexes.get(name, 0)

        # Si el influencer ya ha alcanzado el límite, continúa con el siguiente influencer
        if post_index >= max_downloads_per_influencer:
            print(f"El influencer {name} ya ha alcanzado el límite de {max_downloads_per_influencer} descargas.")
            influencers.remove(influencer)
            del post_indexes[name]
            continue

        print("Descargando post de la cuenta de influencer sobre fitness...")
        print(f"Nombre de la cuenta: {name}")
        print(f"Tipo de influencer: {type}")

        # Crear subdirectorio para el influencer si no existe
        influencer_path = f"{type}/{name}"
        if not os.path.exists(influencer_path):
            os.makedirs(influencer_path)

        try:
            # Descargar posts en el subdirectorio del influencer
            posts = instaloader.Profile.from_username(L.context, name).get_posts()
        except ProfileNotExistsException:
            print(f"El perfil {name} no existe.")
            influencers.remove(influencer)  # remove the non-existing influencer from the list
            continue
        except instaloader.exceptions.ConnectionException as e:
            if '401' in str(e):
                print(f"Error de autenticación al obtener posts de {name}. Comprueba tus credenciales.")
            else:
                print(f"Error de conexión al obtener posts de {name}. Posiblemente bloqueado temporalmente por Instagram.")
            # Guardar la lista actualizada de influencers y post_indexes
            with open('influencers.pkl', 'wb') as f:
                pickle.dump(influencers, f)
            with open('post_indexes.pkl', 'wb') as f:
                pickle.dump(post_indexes, f)
            long_wait_time = random.uniform(1800, 3600)  # espera entre 30 minutos a 1 hora
            print(f"Durmiendo durante {long_wait_time} segundos")
            time.sleep(long_wait_time)
            continue

        for i, post in enumerate(posts):
            if i < post_index:
                continue
            if i - post_index < 11 and influencer_downloads < max_downloads_per_influencer and total_downloads < max_downloads_total:
                try:
                    L.download_post(post, target=influencer_path)
                    total_downloads += 1
                    influencer_downloads += 1
                    influencer_posts_downloaded[name] = influencer_downloads
                    post_indexes[name] = i + 1
                    print(f"{datetime.now()} - Descargada publicación número {i+1} del influencer {name}. Total de publicaciones descargadas: {total_downloads}")
                except ConnectionException as e:
                    print(f"Error descargando la publicación número {i+1} del influencer {name}: {e}")
                else:
                    # Aquí agregamos la pausa entre las peticiones, incluso si la publicación ya fue descargada
                    wait_time = random.uniform(60, 110)  # puedes ajustar el tiempo de espera aquí
                    print(f"Durmiendo durante {wait_time} segundos")                
                    time.sleep(wait_time)
            else:
                break

        if total_downloads >= max_downloads_total:
            print("Se ha alcanzado el máximo de descargas totales. Durmiendo durante una hora...")
            time.sleep(3600) # Sleep for an hour
            total_downloads = 0 # Reset total downloads counter
            # Guardar la lista actualizada de influencers y post_indexes
            with open('influencers.pkl', 'wb') as f:
                pickle.dump(influencers, f)
            with open('post_indexes.pkl', 'wb') as f:
                pickle.dump(post_indexes, f)
            break

        if influencer_downloads >= max_downloads_per_influencer:
            print(f"Se ha alcanzado el máximo de descargas para el influencer {name}. Eliminándolo de la lista...")
            influencers.remove(influencer)

            print(f"Influencers restantes: {len(influencers)}")
            print(f"Nombres: {', '.join([i.split(':')[0] for i in influencers])}\n")
            continue

        # Al final de cada iteración, guardar la lista actualizada de influencers
        with open('influencers.pkl', 'wb') as f:
            pickle.dump(influencers, f)

         # Después de procesar cada influencer, guardar post_indexes
        with open('post_indexes.pkl', 'wb') as f:
            pickle.dump(post_indexes, f)   

    if not influencers:
        print("Todos los influencers han alcanzado su máximo de descargas. Finalizando...")
        break

    print("\n")

