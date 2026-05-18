(defproject decision-engine "1.0.0"
  :dependencies [[org.clojure/clojure "1.11.1"]
                 [ring/ring-core "1.11.0"]
                 [ring/ring-jetty-adapter "1.11.0"]
                 [compojure "1.7.1"]
                 [cheshire "5.12.0"]
                 [ring/ring-json "0.5.1"]]
  :main decision-engine.core)
