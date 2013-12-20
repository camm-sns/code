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
  template=template.replace( '_DESCRIPTORS_', "\t\'" + "\'\t\'".join(sorted(names)) + "\'" )
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

def populate_fixed(template,free_params):
  """Use the list of free parameters to substitute in the
  'variables' section of the init file
  Order alphabetically
  """
  names=[param._name for param in free_params]
  template=template.replace('_NFIX_',str(len(names)))
  if len(names) > 0:
    template=template.replace( '_FIXDESCRIPTORS_', "\t\t\'" + "\'\t\'".join(sorted(names)) + "\'" )
  else:
    template=template.replace( '_FIXDESCRIPTORS_', "" )
  order=sorted(range(len(names)), key = names.__getitem__) #python magic :)
  fields={'_init':'_FIXINITIAL_POINT_',
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
  parser.add_argument('--paramexclude', help='optional, string containing space-separated parameters which will not be optimized')
  args=parser.parse_args()
  paramexclude=[]
  if args.paramexclude: paramexclude=args.paramexclude.split()

  #Dakota input template file
  template="""
# DAKOTA INPUT FILE: nohup dakota dakota.in &

method,
        nl2sol
          initial_trust_radius = 100
          function_precision = 1e-3
          output debug

variables,
        continuous_state = _NFIX_
          initial_state _FIXINITIAL_POINT_
          descriptors  _FIXDESCRIPTORS_
        continuous_design = _NVAR_
          cdv_initial_point _INITIAL_POINT_
          cdv_lower_bounds   _LOWER_BOUNDS_
          cdv_upper_bounds   _UPPER_BOUNDS_
          cdv_descriptors   _DESCRIPTORS_

interface,
        fork
          analysis_driver = 'opt_driver'
            parameters_file = 'params.in'
            results_file = 'results.out'
            file_tag
            file_save

responses,
        calibration_terms = 1500
        analytic_gradients
        no_hessians
"""

  from molmec.ffupdate.ff_update import loadFFtpl
  params=loadFFtpl(args.fftpl)[0] #list of FFParam objects
  free_params=[param for param in params if not param._name in paramexclude]
  template=populate_variables(template,free_params)
  free_params=[param for param in params if param._name in paramexclude]
  template=populate_fixed(template,free_params)

  open(args.outf,'w').write(template)
