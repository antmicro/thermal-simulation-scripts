#!/bin/bash  
DESIGN_PATH=$1
COEF_TYPE=emissivity
COEF_MIN=0
COEF_MAX=1
COEF_STEP=0.1
ISSUE="#"

for ((coef=COEF_MIN; coef<=COEF_MAX; coef=coef+COEF_STEP))
do
echo setting $COEF_TYPE to $coef
tpre set-coef designs/"$DESIGN_PATH" --coef-value $coef --coef-type $COEF_TYPE
git add "$DESIGN_PATH"
git commit -m "[$ISSUE] $(basename "$DESIGN_PATH"), $COEF_TYPE=$coef"
git push
done

echo DONE

