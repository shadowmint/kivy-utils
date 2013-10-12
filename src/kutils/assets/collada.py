from __future__ import absolute_import
import os.path
import zipfile
import StringIO

from kivy.logger import Logger

from kutils.errors import DependencyError
from kutils.widgets.geometry import GMesh


def load_collada(path):
    """ Load a path as a collada file if possible, and return a collection of GMesh objects. """

    load_dependencies()

    doc = load_collada_document(path)
    rtn = []

    # Load materials; textures and diffuse color entries
    materials = {}
    for mat in doc.materials:
        if type(mat.effect.diffuse).__name__ == 'Map':
            try:
                sampler = mat.effect.diffuse.sampler
                surface = sampler.surface
                materials[mat.name] = surface.image
            except Exception as e:
                Logger.warning('Warning: "%s" has an invalid diffuse material: %s', file, str(e))
        else:
            materials[mat.name] = mat.effect.diffuse

    # Convert numpy arrays into useful data
    def convert(raw):
        if type(raw).__name__ == 'float32' or type(raw) == float:
            return float(raw)
        elif type(raw).__name__ == 'int32':
            return int(raw)
        else:
            output = []
            for i in raw:
                output.append(convert(i))
            return output

    # Read meshes
    for geom in doc.geometries:
        for prim in geom.primitives:
            vertex = prim.vertex
            normal = prim.normal
            uv = prim.texcoordset
            material = materials[prim.material]
            if type(material).__name__ == 'CImage':
                diffuse = (0.0, 0.0, 0.0, 0.0)
                texture = material.path
            else:
                diffuse = convert(material)
                texture = None

            # Aggregate mesh elements
            _index = []
            _vertex = []
            _normal = []
            _uv = []

            for index in range(len(vertex)):
                __vertex = vertex[index]
                __normal = (0, 0, 0)
                if index < len(normal):
                    __normal = normal[index]
                __uv = (0, 0)
                if index < len(uv):
                    __uv = uv[index]
                _vertex.extend(__vertex)
                _normal.extend(__normal)
                _uv.extend(__uv)
                _index.append(index)

            print(_vertex)
            print(_normal)
            print(_uv)
            print(_index)


            mesh = GMesh()
            rtn.append(mesh)

    return rtn


def load_dependencies():
    """ Load dependnecies and add them to the global scope """
    try:
        from collada import Collada
    except Exception as e:
        raise DependencyError('pycollada', e)


def load_collada_document(path):
    """ Takes a .dae or a .dae.zip and appropriately loads the target. """
    if path.endswith('.zip'):
        zip = zipfile.ZipFile(path)
        path = path.replace('.zip', '')
        path = os.path.basename(path)
        content = zip.read(path)
    else:
        with open(path) as fp:
            content = fp.read()
    from collada import Collada
    return Collada(StringIO.StringIO(content))
