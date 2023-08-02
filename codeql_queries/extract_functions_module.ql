// Extracts the functionName, start/endLines, and number of lines 
// for an entire Go module

import go

from Function func
select 
        func.getDeclaration().getFile() as funcFile,
        func.getName() as functionName,
        func.getDeclaration().getLocation().getStartLine() as funcStartLine,
        func.getFuncDecl().getLocation().getEndLine() as funcEndLine,
        func.getDeclaration().getLocation().getNumLines() as funcNumLines,
        func.getQualifiedName() as functionQualifiedName,
        func.getFuncDecl().getLocation() as funcLocation