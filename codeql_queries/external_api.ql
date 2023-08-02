import go
import semmle.go.security.ExternalAPIs

from ExternalApiDataNode externalNode
select 
    externalNode.getFunctionDescription() as functionDescription,
    externalNode.getFunction() as functionName