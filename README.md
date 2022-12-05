# Emulsion - A template CLI tool

## Sources
- Github: Currently the only source defined

## init.emulsion
'init.emulsion' is a file at the root of a project directory which defines directives of what files
to download when the template project is applied to a blank directory. The default directive is 'main' 
unless specified otherwise.

## DotEmulsion structure
An example of an DotEmulsion file can be found as "example.emulsion"
### Directive Instructions
- exclude: Files to exclude when applying the template to the blank directory. (Incompatible with include)
- include: Files to include when applying the template to the blank directory. (Incompatible with exclude)
- settings: Settings which the interpreter will follow run applying the project such as if it should be recursive.
- pre-deps: Dependencies that should be applied before the current project should be applied.
- post-deps: Dependencies that should be applied after the current project is applied.
- run: Directives that should be applied before the current directive in run.

### Directive Instructions order
When applying a DotEmulsion template the order is the following:  
run -> pre-deps -> project -> post-deps
