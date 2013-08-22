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
  template="""
# DAKOTA INPUT FILE: nohup dakota dakota.in &

method,
        nl2sol
          initial_trust_radius = 100
          function_precision = 1e-3
          output debug

variables,
        continuous_state = 1
          initial_state 0.0
          descriptors  'b1'
        continuous_design = 7
          cdv_initial_point 7.261128286320040e-01 1.000000000000000e-08 5.509589221505974e-02 4.438857367328487e-02 3.659833517176896e-02 2.206616918284543e-04 4.170000000000000e-01
          cdv_lower_bounds   0.25 1e-8 0.0 0.0 0.0 -4.e-4 0.3
          cdv_upper_bounds   2.0 2e-4 0.1 0.1 0.1 4.e-4 0.5
          cdv_descriptors    'c0' 'b0' 'e0.0' 'e0.1' 'e0.2' 'eshift' 'FF1'

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
  free_params=[param for param in params if param.isFree()]
  template=populate_variables(template,free_params)

  open(args.outf,'w').write(template)
