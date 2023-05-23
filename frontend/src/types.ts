export interface Owner {
  firstname: string
  lastname: string
  organization: string
  is_primary_owner: boolean
}

export interface Thing {
  id: string
  name: string
  owners: Owner[]
  site_type: string
  sampling_feature_code: string
  latitude: number
  longitude: number
  elevation: number
  owns_thing: boolean
  follows_thing: boolean
  description: string
  sampling_feature_type: string
  state: string
  county: string
  is_primary_owner: boolean
  followers: number
}

export interface Datastream {
  id: string
  thing_id: string
  observation_type: string
  result_type: string
  status: string
  sampled_medium: string
  no_data_value: number
  aggregation_statistic: string
  observations: Observation[]
  most_recent_observation: any
  unit_id: string
  unit_name: string
  observed_property_id: string
  observed_property_name: string
  method_id: string
  method_name: string
  processing_level_id: string
  processing_level_name: string
  is_visible: boolean
}

export interface Observation {
  id: string
  result: string
  result_time: string
}

export interface Unit {
  id: string
  person_id: string
  name: string
  symbol: string
  definition: string
  unit_type: string
}

export interface Sensor {
  id: string
  name: string
  description: string
  manufacturer: string
  model: string
  method_type: string
  method_code: string
  method_link: string
  encoding_type: string
  model_url: string
}

export interface ObservedProperty {
  id: string
  name: string
  definition: string
  description: string
  variable_type: string
  variable_code: string
}

export interface ProcessingLevel {
  id: string
  person_id: string
  processing_level_code: string
  definition: string
  explanation: string
}

export interface User {
  id: string
  email: string
  first_name: string
  middle_name: string
  last_name: string
  phone: string
  address: string
  organization: string
  type: string
}
