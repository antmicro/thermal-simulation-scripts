#!/bin/bash  
DESIGN_PATH=$1
COEF_TYPE=emissivity # 'emissivity' or 'film'
COEF_MIN=0
COEF_MAX=0.3
COEF_STEP=0.1
ISSUE="" # Without "#"

# for ((coef=COEF_MIN; coef<=COEF_MAX; coef=coef+COEF_STEP))
for coef in $(seq $COEF_MIN $COEF_STEP $COEF_MAX)
do
echo setting $COEF_TYPE to "$coef"
tpre set-coef --fcstd "$DESIGN_PATH" --coef-value "$coef" --coef-type $COEF_TYPE
git add "$DESIGN_PATH"
git commit -m "[#$ISSUE] $(basename "$DESIGN_PATH"), $COEF_TYPE=$coef"
git push
done

echo DONE

