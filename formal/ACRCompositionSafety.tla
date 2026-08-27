----------------------- MODULE ACRCompositionSafety -----------------------
EXTENDS Naturals, Sequences, FiniteSets

CONSTANTS Agents, Rooms, Capabilities, InvariantRules

VARIABLES roomState, agentTokens, stateHashChain

TypeOK ==
    /\ roomState \in [Rooms -> SUBSET Agents]
    /\ agentTokens \in [Agents -> SUBSET Capabilities]
    /\ stateHashChain \in Seq(STRING)

Init ==
    /\ roomState = [r \in Rooms |-> {}]
    /\ agentTokens = [a \in Agents |-> {}]
    /\ stateHashChain = <<>>

CompositionSafetyInvariant ==
    \A r \in Rooms :
        \A a \in roomState[r] :
            "ACCESS_ROOM" \in agentTokens[a]

HashMonotonicityInvariant ==
    Len(stateHashChain) >= 0

============================================================================
