(ns decision-engine.rules
  (:import [java.time LocalDate]
           [java.time.temporal ChronoUnit]))


(defn parse-date [value]
  (cond
    (instance? LocalDate value) value
    (string? value) (LocalDate/parse value)
    :else (throw (ex-info "Invalid date value" {:value value}))))


(defn days-between [start-date end-date]
  (inc (.between ChronoUnit/DAYS (parse-date start-date) (parse-date end-date))))


(defn before-today? [value]
  (.isBefore (parse-date value) (LocalDate/now)))


(def rules
  [{:name "Equipment must be available"
    :weight 100
    :hard-block true
    :check (fn [ctx] (= (:equipment-status ctx) "available"))}

   {:name "Rental period must not exceed maximum allowed days"
    :weight 40
    :check (fn [ctx]
             (<= (days-between (:start-date ctx) (:end-date ctx))
                 (:equipment-max-rental-days ctx)))}

   {:name "Start date must not be in the past"
    :weight 30
    :hard-block true
    :check (fn [ctx]
             (not (before-today? (:start-date ctx))))}

   {:name "User must have no overdue rentals"
    :weight 35
    :hard-block true
    :check (fn [ctx] (= (:user-overdue-rentals ctx) 0))}

   {:name "Student cannot have more than 3 active rentals"
    :weight 25
    :hard-block true
    :check (fn [ctx]
             (or (not= (:user-role ctx) "student")
                 (< (:user-active-rentals ctx) 3)))}

   {:name "Staff cannot have more than 5 active rentals"
    :weight 20
    :hard-block true
    :check (fn [ctx]
             (or (not= (:user-role ctx) "staff")
                 (< (:user-active-rentals ctx) 5)))}

   {:name "Servers and cameras require staff role or higher"
    :weight 50
    :check (fn [ctx]
             (or (not (contains? #{"server" "camera"} (:equipment-type ctx)))
                 (contains? #{"staff" "equipment_manager" "admin"} (:user-role ctx))))}])


(defn evaluate [ctx]
  (if (contains? #{"staff" "equipment_manager" "admin"} (:user-role ctx))
    {:approved true
     :score 100
     :reasons []}
    (let [failed      (filter #(not ((:check %) ctx)) rules)
          hard-blocks (filter :hard-block failed)
          penalty     (reduce + (map :weight failed))
          score       (max 0 (- 100 penalty))
          approved    (and (empty? hard-blocks) (>= score 60))]
      {:approved approved
       :score score
       :reasons (vec (map :name failed))})))


(defn public-rules []
  (vec
   (map
    (fn [rule]
      {:name (:name rule)
       :weight (:weight rule)
       :hardBlock (boolean (:hard-block rule))})
    rules)))
