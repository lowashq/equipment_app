(ns decision-engine.handler
  (:require [cheshire.core :as json]
            [compojure.core :refer [GET POST defroutes]]
            [compojure.route :as route]
            [decision-engine.rules :as rules]
            [ring.util.response :as response]))


(defn json-response
  ([payload] (json-response 200 payload))
  ([status payload]
   (-> (response/response (json/generate-string payload))
       (response/status status)
       (response/content-type "application/json"))))


(defn value-for [payload camel-key snake-key]
  (or (get payload camel-key)
      (get payload snake-key)))


(defn normalize-context [payload]
  {:user-id (value-for payload :userId :user_id)
   :equipment-id (value-for payload :equipmentId :equipment_id)
   :start-date (value-for payload :startDate :start_date)
   :end-date (value-for payload :endDate :end_date)
   :user-role (value-for payload :userRole :user_role)
   :user-active-rentals (or (value-for payload :userActiveRentals :user_active_rentals) 0)
   :user-overdue-rentals (or (value-for payload :userOverdueRentals :user_overdue_rentals) 0)
   :equipment-status (value-for payload :equipmentStatus :equipment_status)
   :equipment-max-rental-days (or (value-for payload :equipmentMaxRentalDays :equipment_max_rental_days) 0)
   :equipment-type (value-for payload :equipmentType :equipment_type)})


(defn parse-json-body [request]
  (try
    (json/parse-string (slurp (:body request)) true)
    (catch Exception _
      nil)))


(defn decide [request]
  (if-let [payload (parse-json-body request)]
    (try
      (json-response (rules/evaluate (normalize-context payload)))
      (catch Exception ex
        (json-response 400 {:approved false
                            :score 0
                            :reasons [(str "Invalid request: " (.getMessage ex))]})))
    (json-response 400 {:approved false
                        :score 0
                        :reasons ["Invalid JSON body"]})))


(defroutes app
  (GET "/health" [] (json-response {:status "ok"}))
  (GET "/rules" [] (json-response (rules/public-rules)))
  (POST "/decide" request (decide request))
  (route/not-found (json/generate-string {:detail "Not found"})))
