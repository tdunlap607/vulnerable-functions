import go
from DataFlow::CallNode caller
select
    caller.getEnclosingCallable().getFuncDef().getName() as callerFunction,
    caller.getEnclosingCallable().getFuncDef().getLocation() as callerLocation,
    caller.getEnclosingCallable().getFuncDef().getFile() as callerFunctionFile,
    caller.getEnclosingCallable().getFuncDef().getLocation().getStartLine() as callerFunctionStartLine,
    caller.getCalleeName() as calleeFunction,
    caller.getCalleeNode().getAPredecessor().getFile() as calleeFunctionFile,
    caller.getCalleeNode().getAPredecessor().getStartLine() as calleeFunctionStartLine,
    caller.getCalleeNode().getAPredecessor().getEndLine() as calleeFunctionEndLineTest


