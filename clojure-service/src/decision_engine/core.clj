(ns decision-engine.core
  (:require [decision-engine.handler :refer [app]]
            [ring.adapter.jetty :refer [run-jetty]])
  (:gen-class))


(defn -main [& _args]
  (println "Starting Decision Engine on port 3001")
  (run-jetty app {:port 3001 :join? true}))
