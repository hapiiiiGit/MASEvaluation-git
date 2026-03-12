import json
import os
from typing import List, Dict, Any, Optional
from jsonschema import validate, ValidationError

# JSON schema for PlayerModel
PLAYER_MODEL_SCHEMA = {
    "type": "object",
    "required": ["name", "vertices", "faces", "rig", "metadata", "textures"],
    "properties": {
        "name": {"type": "string"},
        "vertices": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["x", "y", "z", "weights", "bone_indices"],
                "properties": {
                    "x": {"type": "number"},
                    "y": {"type": "number"},
                    "z": {"type": "number"},
                    "weights": {
                        "type": "array",
                        "items": {"type": "number"}
                    },
                    "bone_indices": {
                        "type": "array",
                        "items": {"type": "integer"}
                    }
                }
            }
        },
        "faces": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["v1", "v2", "v3"],
                "properties": {
                    "v1": {"type": "integer"},
                    "v2": {"type": "integer"},
                    "v3": {"type": "integer"}
                }
            }
        },
        "rig": {
            "type": "object",
            "required": ["bones", "constraints"],
            "properties": {
                "bones": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["name", "parent", "head", "tail"],
                        "properties": {
                            "name": {"type": "string"},
                            "parent": {"type": "integer"},
                            "head": {
                                "type": "array",
                                "items": {"type": "number"},
                                "minItems": 3,
                                "maxItems": 3
                            },
                            "tail": {
                                "type": "array",
                                "items": {"type": "number"},
                                "minItems": 3,
                                "maxItems": 3
                            }
                        }
                    }
                },
                "constraints": {"type": "object"}
            }
        },
        "metadata": {"type": "object"},
        "textures": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["type", "dds_path"],
                "properties": {
                    "type": {"type": "string"},
                    "dds_path": {"type": "string"}
                }
            }
        }
    }
}


class Vertex:
    def __init__(self, x: float, y: float, z: float,
                 weights: List[float], bone_indices: List[int]):
        self.x = x
        self.y = y
        self.z = z
        self.weights = weights
        self.bone_indices = bone_indices

    def to_dict(self) -> Dict[str, Any]:
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "weights": self.weights,
            "bone_indices": self.bone_indices
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Vertex':
        return Vertex(
            x=data["x"],
            y=data["y"],
            z=data["z"],
            weights=data.get("weights", []),
            bone_indices=data.get("bone_indices", [])
        )


class Face:
    def __init__(self, v1: int, v2: int, v3: int):
        self.v1 = v1
        self.v2 = v2
        self.v3 = v3

    def to_dict(self) -> Dict[str, Any]:
        return {
            "v1": self.v1,
            "v2": self.v2,
            "v3": self.v3
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Face':
        return Face(
            v1=data["v1"],
            v2=data["v2"],
            v3=data["v3"]
        )


class Bone:
    def __init__(self, name: str, parent: int,
                 head: List[float], tail: List[float]):
        self.name = name
        self.parent = parent
        self.head = head
        self.tail = tail

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "parent": self.parent,
            "head": self.head,
            "tail": self.tail
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Bone':
        return Bone(
            name=data["name"],
            parent=data["parent"],
            head=data.get("head", [0.0, 0.0, 0.0]),
            tail=data.get("tail", [0.0, 0.0, 0.0])
        )


class RigData:
    def __init__(self, bones: List[Bone], constraints: Dict[str, Any]):
        self.bones = bones
        self.constraints = constraints

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bones": [bone.to_dict() for bone in self.bones],
            "constraints": self.constraints
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'RigData':
        bones = [Bone.from_dict(b) for b in data.get("bones", [])]
        constraints = data.get("constraints", {})
        return RigData(bones, constraints)


class TextureMap:
    def __init__(self, type_: str, dds_path: str, data: Optional[bytes] = None):
        self.type = type_
        self.dds_path = dds_path
        self.data = data  # Raw DDS bytes, not serialized in JSON

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "dds_path": self.dds_path
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'TextureMap':
        return TextureMap(
            type_=data["type"],
            dds_path=data["dds_path"]
        )


class PlayerModel:
    def __init__(self,
                 name: str,
                 vertices: List[Vertex],
                 faces: List[Face],
                 rig: RigData,
                 metadata: Dict[str, Any],
                 textures: List[TextureMap]):
        self.name = name
        self.vertices = vertices
        self.faces = faces
        self.rig = rig
        self.metadata = metadata
        self.textures = textures

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "vertices": [v.to_dict() for v in self.vertices],
            "faces": [f.to_dict() for f in self.faces],
            "rig": self.rig.to_dict(),
            "metadata": self.metadata,
            "textures": [t.to_dict() for t in self.textures]
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'PlayerModel':
        vertices = [Vertex.from_dict(v) for v in data.get("vertices", [])]
        faces = [Face.from_dict(f) for f in data.get("faces", [])]
        rig = RigData.from_dict(data.get("rig", {}))
        metadata = data.get("metadata", {})
        textures = [TextureMap.from_dict(t) for t in data.get("textures", [])]
        name = data.get("name", "")
        return PlayerModel(name, vertices, faces, rig, metadata, textures)

    @staticmethod
    def from_json(json_path: str) -> 'PlayerModel':
        if not os.path.exists(json_path):
            raise FileNotFoundError(f"JSON file not found: {json_path}")
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        try:
            validate(instance=data, schema=PLAYER_MODEL_SCHEMA)
        except ValidationError as e:
            raise ValueError(f"JSON validation error: {e.message}")
        return PlayerModel.from_dict(data)

    def to_json(self, json_path: str):
        data = self.to_dict()
        try:
            validate(instance=data, schema=PLAYER_MODEL_SCHEMA)
        except ValidationError as e:
            raise ValueError(f"JSON validation error: {e.message}")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)