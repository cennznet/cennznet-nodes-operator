# cennznet-nodes-operator

- to install/upgrade the operator

    ```
  kubectl config use-context eks-prod
  helm upgrade --install eks-sg-operator-release  chart -n aws-sg-cennznet-validators-operator --debug

  kubectl config use-context aks-mainnet-us
  helm upgrade --install az-us-operator-release  chart -n az-us-cennznet-validators-operator  --debug
  
  kubectl config use-context aks-mainnet-ie
  kubectl create ns az-ie-cennznet-validators-operator
  kubectl create secret generic operator-secret --from-file=/tmp/secret.json -n az-ie-cennznet-validators-operator
  helm upgrade --install az-ie-operator-release  chart -n az-ie-cennznet-validators-operator  --debug
  kubectl create clusterrolebinding cluster-admin-binding-4-operator --clusterrole cluster-admin  --user "system:serviceaccount:az-ie-cennznet-validators-operator:cennznet-validator-operator-service-account"
    ```