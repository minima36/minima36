# -*- coding: utf-8 -*-
"""
Created on Thu Jan 25 21:06:14 2024

@author: Minima

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! NOTE !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
LES POSITIONS INITIALES SONT EN BLEU
LES POSITIONS INITIALES DEPLACES VERS NOUVEAUX POINTS DE SURFACE INFERIEURE SONT EN BLEU
LES EMPLACEMENTS FINAUX EN VERT
LES POSITIONS FINALES (LES POINTS QUI ONT ETE DEPLACES) SONT EN ROUGE

"""
import numpy as np

arrangement_init = [(8,8),(1.3,4),(14,6),(8,4),(14,2),(2.4,7)]
arrangement_final = [(11.0,4.6),(5.0,4.6),(17.0,4.6),(17.0,1.8),(17.0,7.4), (11.0,7.4)]
surface_inf = [[(2.0, 1.8), (5.0, 1.8), (8.0, 1.8), (11.0, 1.8), (14.0, 1.8), (17.0, 1.8)], [(2.0, 4.6), (5.0, 4.6), (8.0, 4.6), (11.0, 4.6), (14.0, 4.6), (17.0, 4.6)], [(2.0, 7.4), (5.0, 7.4), (8.0, 7.4), (11.0, 7.4), (14.0, 7.4), (17.0, 7.4)]]
rayon = 1

def deplacer(A, B, T):
    # Déplcer le point A à l'emplacement B mais en vérifiant qu'il n'y a aucune collision tout au long de la trajectoire (A,B)
    for O in T:
        # pour chaque point de l'ensemble T, on vérifie qu'il n'y a aucune collision avec A lors de son déplacement vers B
        pt_intersection = intersection_droite_cercle(A, B, O, rayon)
        #print(pt_intersection)
        if len(pt_intersection) > 0 :
            # Si il y a une collision alors le point A ne bouge pas, on le renvoit lui-même
            return []
        # dans le cas où y a aucun obstacle en route alors on déplace le point A vers B
    return B

#Deplacement vers point quelconque vers un point de Pt
def deplacer_vers_surface(arrangement_initial, surface_inferieure):
    nouveaux_points = []

    for point in arrangement_initial:
        x, y = point
        point_initial = np.array([x, y])

        # Recherche du point le plus proche dans la surface inférieure
        distances = [np.linalg.norm(np.array(surface_point) - point_initial) for surface_point in surface_inferieure]
        indice_plus_proche = np.argmin(distances)
        point_plus_proche = np.array(surface_inferieure[indice_plus_proche])

        nouveaux_points.append(point_plus_proche)

    return nouveaux_points


from shapely.geometry import LineString
from shapely.geometry import Point
def cercles_intersect(x1, y1, rayon1, x2, y2, rayon2):
    #On détermine si deux cercles ont une intersection (une façon de gérer les collisions entre objets)
    p1 = Point(x1, y1)
    c1 = p1.buffer(rayon1).boundary
    
    p2 = Point(x2, y2)
    c2 = p2.buffer(rayon2).boundary
    
    return c1.intersects(c2)

def intersection_droite_cercle(A, B, O, r):

    #points d'intersections entre un segment [AB] et un cercle C de centre O et de rayon r
    # On crée le point O, centre du cercle
    p = Point(O)
    # On crée le cercle c de centre p et de rayon r
    c = p.buffer(r).boundary
    # On crée le segment allant du point A au point B
    l = LineString([A, B])
    # On vérifie si le segment l et le cercle c se croisent
    i = c.intersects(l)
    tex = []
    if(i):
        # si il y a intersection on détermine les points d'intersections
        inter = c.intersection(l)
        if(type(inter) == Point):
            tex.append(inter.x)
            tex.append(inter.y)
        else:
            N = len(inter.geoms)
            for k in range(0, N):
                tex.append([inter.geoms[k].x, inter.geoms[k].y])
    return tex

# On décalle un peu les valeur des points pour ne pas que les cercles soient confondus (on ajoute 0.25 à chaque coordonnée)    
arrangement = np.add(arrangement_init, 0.25)
for k in range(0, len(arrangement)):
    tentatives = 0
    echecs = 0
    stop = False #stop permet d'arrêter l'itération des boucles imbriquée si la bonne position est trouvée
    tmp = np.delete(arrangement, k, 0) #tmp est l'ensemble de tous les points déplaçables mis à part celui qu'on est entrain de vouloir déplacer et celui à la position k dans la liste
    print("\n\n>>>>>>>> Point ", (k+1), " <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
    for i in range(0, len(surface_inf)):
        for j in range(0, len(surface_inf[i])):
            #print("i: ", i, " j: ", j)
            tentatives = tentatives + 1
            A_i = deplacer(arrangement[k], surface_inf[i][j], tmp)
            if np.array_equal(A_i, []):
                echecs = echecs + 1
                print("pas de déplacement sur l'emplacement (", (i+1), ",", (j+1), ") car il y a une collision")
            else: 
                if (cercles_intersect(A_i[0], A_i[1], rayon, arrangement_final[k][0], arrangement_final[k][1], rayon)):
                    arrangement[k] = A_i
                    print("déplacement éffectué avec succès  du point ", (k+1), " dans son emplacement final (", (i+1), ",", (j+1), ")")
                    stop = True
                else:
                    echecs = echecs + 1
                    print("pas de déplacement sur l'emplacement (", (i+1), ",", (j+1), ") car emplacement non final")
                if stop:
                    break
        if stop:
            break
    print(">>>>> tentatives: ", tentatives, " | echecs: ", echecs, " <<<<<<<<<<<<<<<<<<<<<<<<\n")
# je décale un peu les points finaux pour qu'on différencie avec les emplacements
arrangement = np.add(arrangement, 0.25)

#----------------------------------------------------------------------------------------------------------------
#Affichage de Surface inferieure et des arrangements
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import pylab as pl
def afficher_surface_et_arrangements(l, L, m_l, m_L, Surface_inferieure, arrangement_initial, nouveaux_points, arrangement, arrangement_final, r, namefile):
    if m_l <= 0 or m_L <= 0:
        print("Les dimensions de Surface_inferieure sont incorrectes.")
        return

    fig, ax = plt.subplots()

    # Afficher Surface_inferieure en pointillés
    for i in range(int(m_l)):
        for j in range(int(m_L)):
            #if j < len(Surface_inferieure[i]):  # Verifier si j est dans la plage valide pour Surface_inferieure[i]
            x = Surface_inferieure[i][j][0]
            y = Surface_inferieure[i][j][1]
            drawing = plt.Circle((x, y), r, linestyle='dotted', fill=False)
            ax.add_artist(drawing)
             
    # Afficher arrangement_initial en bleu
    nbr = 0
    for point in arrangement_initial:
        x, y = point
        drawing = plt.Circle((x, y), r, color='blue', fill=True)
        ax.add_artist(drawing)
        nbr = nbr + 1
        pl.text(x, y, str(nbr), color="white", fontsize=16)
        
    #Afficher nouveaux points dépacés en jaune
    for point in nouveaux_points:
        x, y = point
        drawing = plt.Circle((x, y), 0.1, color='yellow', fill=True)
        ax.add_artist(drawing)
        
        plt.show()
    
    
    # Afficher arrangement_final en vert
    nbr = 0
    for point in arrangement_final:
        x, y = point
        drawing = plt.Circle((x, y), r, color='green', fill=True)
        ax.add_artist(drawing)
        nbr = nbr + 1
        pl.text(x, y, str(nbr), color="white", fontsize=16)
        
    # Afficher arrangement en rouge
    nbr = 0
    for point in arrangement:
        x, y = point
        drawing = plt.Circle((x, y), r, color='red', fill=True)
        ax.add_artist(drawing)
        nbr = nbr + 1
        pl.text(x, y, str(nbr), color="black", fontsize=16)

    ax.set_aspect(1)
    ax.add_patch(Rectangle((0, 0), L, l, fill=False))
    plt.title(f'Surface inferieure et Arrangements - {namefile}')
    plt.xlim(0, L)
    plt.ylim(0, l)
    plt.savefig(f'{namefile}-SurfaceEtArrangements.png')
    plt.show()
#-------------------------------------------------------------------------------------------------------------

afficher_surface_et_arrangements(10,20,3,6, surface_inf, arrangement_init, nouveaux_points, arrangement, arrangement_final, rayon, "Instance-1")