import re as mod_re
import os as mod_os

BLUE = '\\textcolor{{blue}}{{{0}}}'
BLACK = '\\textcolor{{black}}{{{0}}}'
RED = '\\textcolor{{red}}{{{0}}}'
GREEN = '\\textcolor{{green}}{{{0}}}'
GRAY = '\\textcolor{{gray}}{{{0}}}'

types = {
		'\$\s+git\s+status.*': (
				( '^(#\t)(.*)$', ( GRAY, BLUE ) ),
		),
}

def to_latex_string( string ):
	string = string.replace( ' ', '\\ ' )
	string = string.replace( '$', '\\$' )
	string = string.replace( '#', '\\#' )
	string = string.replace( '_', '\\_' )
	string = string.replace( '\t', '\ \ \ \ \ \ \ \ ' )
	string = string.replace( '<', '$<$' )
	string = string.replace( '>', '$>$' )

	return string

def unnest( list_or_tuple ):
	if isinstance( list_or_tuple, list ) or isinstance( list_or_tuple, tuple ):
		result = []
		for item in list_or_tuple:
			result += unnest( item )
		return result
	else:
		return [ list_or_tuple ]

def process_groups_and_roules( groups, rules ):
	result = ''

	#print 'groups:', groups
	#print 'rules:', rules

	for i in range( len( groups ) ):
		group = groups[ i ]
		rule = rules[ i ]

		#print 'group:', group
		#print 'rule:', rule

		result += rule.format( group )

	return result

def execute_git_status_rules( string, type_rules ):
	result = ''
	rules = [ 
		( '^(\$\s*)(.*)$', ( GRAY, BLACK ) ),
		( '^(.*)$', ( GRAY ) ),
	]
	for rule in type_rules:
		rules.insert( 0, rule )
	for line in string.split( '\n' ):
		found = False
		for item in rules:
			rule_regex = item[ 0 ]
			rule_template = item[ 1 : ]
			if not found and mod_re.match( rule_regex, line ):
				groups = mod_re.findall( rule_regex, line )
				assert len( groups ) == 1
				assert len( groups ) == len( rule_template )

				result += to_latex_string( process_groups_and_roules( unnest( groups ), unnest( rule_template ) ) ) + '\\\\%\n'

				found = True
		if not found:
			raise Exception( 'No rule for line: {0}'.format( line ) )
	
	return result

def to_latex( string ):
	for type_regex, type_rules in types.items():
		if mod_re.match( type_regex, string ):
			return '\\noindent%\n\\texttt{%\n' + execute_git_status_rules( string, type_rules ) + '}\n'
	raise Exception( 'Unknown git output for {0}'.format( string ) )

if __name__ == '__main__':
	for file_name in mod_os.listdir( 'git_output' ):
		if file_name.endswith( '.txt' ):
			with file( 'git_output/{0}'.format( file_name ) ) as f:
				content = f.read()
			latex = to_latex( content )
			latex_file_name = file_name.replace( '.txt', '.tex' )
			with file( 'git_output/{0}'.format( latex_file_name ), 'w' ) as f:
				f.write( latex )
			print latex_file_name, 'OK'
