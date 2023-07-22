

import json
from math import cos, pi, sin
import parameters


class PrefabReader:
	def __init__(self, filename) -> None:
		with open(filename) as f:
			self.__prefabs = json.load(f)
	
	def next_prefab(self) -> dict:
		return self.__prefabs.pop(0)
	
	def has_prefab(self) -> bool:
		return len(self.__prefabs) > 0

from dataclasses import dataclass

@dataclass
class Vector3:
	x: float
	y: float
	z: float

	def __add__(self, other):
		return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)

	def __sub__(self, other):
		return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)

	def __mul__(self, other):
		return Vector3(self.x * other, self.y * other, self.z * other)

	def __truediv__(self, other):
		return Vector3(self.x / other, self.y / other, self.z / other)

	def tilt_around_z(self, angle, point):
		angle_radians = angle * pi / 180.0
		cosine = cos(angle_radians)
		sine = sin(angle_radians)

		self.x -= point.x
		self.y -= point.y
  
		x = self.x * cosine - self.y * sine
		y = self.x * sine + self.y * cosine
  
		self.x = x + point.x
		self.y = y + point.y
  
		return self

  

@dataclass
class Vector3i:
	x: int
	y: int
	z: int

class PrefabBuilder:
	def __init__(self, prefab) -> None:
		self.__prefab = prefab
		
	def get_prefab_name(self) -> str:
		pf = self.__prefab
		name = f"{pf['type']}_elevation{pf['elevation']}_tilt{pf['tilt_start']}-{pf['tilt_end']}_slope{pf['slope_start']}-{pf['slope_end']}{('curve' + pf['forward'] + '-' + pf['sideways']) if pf['type'] == 'curve' else ''}"
	
		return name
	
	def generate_face_list(self) -> list:
		face_list: list[Vector3i] = []

		for i in range(1, parameters.OBJ_RESOLUTION + 1):
			face_list.append(Vector3i(i, i + 1, i + parameters.OBJ_RESOLUTION + 1))
			face_list.append(Vector3i(i + parameters.OBJ_RESOLUTION + 1, i + 1, i + parameters.OBJ_RESOLUTION + 1 + 1))

		return face_list
	
	def tilt_vertices(self, left_vertices, right_vertices, tilt_start, tilt_end, pivot):
		for index in range(len(left_vertices)):
			current_tilt = tilt_start + (tilt_end - tilt_start) * index / parameters.OBJ_RESOLUTION
			left_vertices[index].tilt_around_z(current_tilt, pivot)
			right_vertices[index].tilt_around_z(current_tilt, pivot)

	def write_straight(self, prefab_name, division_points):

		elevation = self.__prefab['elevation']
  
		left_vertices = [Vector3(0, 0, parameters.PREFAB_WIDTH * point) for point in division_points]
		right_vertices = [Vector3(parameters.PREFAB_WIDTH, 0, parameters.PREFAB_WIDTH * point) for point in division_points]

		left_normals = [Vector3(0, 1, 0) for _ in division_points]
		right_normals = [Vector3(0, 1, 0) for _ in division_points]

		if self.__prefab['tilt_start'] != 0 or self.__prefab['tilt_end'] != 0:
			self.tilt_vertices(left_vertices, right_vertices, self.__prefab['tilt_start'], self.__prefab['tilt_end'], Vector3(parameters.PREFAB_WIDTH / 2, 0, 0))
			self.tilt_vertices(left_normals, right_normals, self.__prefab['tilt_start'], self.__prefab['tilt_end'], Vector3(0, 0, 0))

		for index in range(len(left_vertices)):
			left_vertices[index].y += parameters.PREFAB_HEIGHT * division_points[index] * elevation
			right_vertices[index].y += parameters.PREFAB_HEIGHT * division_points[index] * elevation
  
		faces = self.generate_face_list()

		with open(f"prefabs/{prefab_name}.obj", "w") as f:	
			for vertex in left_vertices:
				f.write(f'v {vertex.x} {vertex.y} {vertex.z}\n')

			for vertex in right_vertices:
				f.write(f'v {vertex.x} {vertex.y} {vertex.z}\n')

			# for normal in normals:
			# 	f.write(f'vn {normal[0]} {normal[1]} {normal[2]}\n')
   
			for normal in left_normals:
				f.write(f'vn {normal.x} {normal.y} {normal.z}\n')
			
			for normal in right_normals:
				f.write(f'vn {normal.x} {normal.y} {normal.z}\n')

			# for tex_coord in texture_coords:
			# 	f.write(f'vt {tex_coord[0]} {tex_coord[1]}\n')

			for face in faces:
				# f.write(f'f {face.x} {face.y} {face.z}\n')
				f.write(f'f {face.x}//{face.x} {face.y}//{face.y} {face.z}//{face.z}\n')
 
	def write_obj(self):
		prefab_name = self.get_prefab_name()

		division_points = [x / parameters.OBJ_RESOLUTION for x in range(0, parameters.OBJ_RESOLUTION + 1)]
		
		prefab_type = self.__prefab['type']
  
		if prefab_type == 'straight':
			self.write_straight(prefab_name, division_points)
			return
		elif prefab_type == 'curve':
			self.write_curve(prefab_name, division_points)
  
		

def main() -> None:
	prefab_reader = PrefabReader("track_prefabs.JSON")
	
	while prefab_reader.has_prefab():
		prefab = prefab_reader.next_prefab()
		prefab_builder = PrefabBuilder(prefab)
		prefab_builder.write_obj()

	

if __name__ == "__main__":
	main()