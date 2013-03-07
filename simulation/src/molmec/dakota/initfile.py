'''
Created on Dec 26, 2012

Generate the initial Dakota input file 
'''
#from pdb import set_trace as trace # only for purposes of debugging 

def populate_variables(template,free_params):
  """Use the list of free parameters to substitute in the
  'variables' section of the init file
  Order alphabetically
  """
  names=[param._name for param in free_params]
  template=template.replace('_NVAR_',str(len(names)))
  template=template.replace( '_DESCRIPTORS_', "\t"+"\t".join(sorted(names)) )
  order=sorted(range(len(names)), key = names.__getitem__) #python magic :)
  fields={'_init':'_INITIAL_POINT_',
          '_minimum':'_LOWER_BOUNDS_',
          '_maximum':'_UPPER_BOUNDS_',
          '_tolerance':'_MAX_STEP_',
          }
  for attribute,field in fields.items():
    values=[param.__getattribute__(attribute) for param in free_params]
    template=template.replace(field, "\t"+"\t".join([str(values[i]) for i in order]))
  return template

if __name__ == '__main__':
  from argparse import ArgumentParser
  parser = ArgumentParser(description='script generating the initial Dakota input file')
  parser.add_argument('--conf', help='configuration file') #this instead of the future GUI
  parser.add_argument('--fftpl',help='name of the XML force field template file')
  parser.add_argument('--outf', help='name of the output Dakota input file')
  args = parser.parse_args()

  #Dakota input template file
  template="""strategy,
  single_method
  graphics,tabular_graphics_data

method,
  dot_mmfd,
  max_iterations = 20,
  convergence_tolerance = 1e-4

variables,
  continuous_design = _NVAR_
  descriptors_DESCRIPTORS_
  initial_point_INITIAL_POINT_
  lower_bounds_LOWER_BOUNDS_
  upper_bounds_UPPER_BOUNDS_
  max_step_MAX_STEP_

interface,
  fork
  results_file = 'results.in'
  input_filter = 'readResultsFile.py'
  analysis_driver = 'intelScript.py'
  output_filter = 'writeParametersFile.py'
  parameters_file = 'parameters.in'

responses,
  objective_functions = 1
  numerical_gradients
  method_source dakota
  interval_type central
  fd_gradient_step_size = 1.e-4
  no_hessians
"""

  from molmec.ffupdate.ff_update import loadFFtpl
  params=loadFFtpl(args.fftpl)[0] #list of FFParam objects
  free_params=[param for param in params if param.isFree()]
  template=populate_variables(template,free_params)

  open(args.outf,'w').write(template)