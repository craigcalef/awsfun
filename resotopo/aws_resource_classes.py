# build a resource topology
from dataclasses import dataclass
import json, sys

@dataclass Resource:
    name: str
    id: str

@dataclass
class Account(Resource):
    regions: dict = {}

@dataclass
class Region(Resource):
    vpcs: dict = {}
    contents: dict = {}

@dataclass 
class VPC(Resource):
    azs: dict = {}
    contents: dict = {}

@dataclass
class AvailabilityZone(Resource):
    subnets: dict

@dataclass
class Subnet(Resource):
    instances: dict
    contents: dict

