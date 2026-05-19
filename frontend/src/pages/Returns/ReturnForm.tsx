import { useForm } from "react-hook-form";

import { ReturnPayload } from "../../api/returns";

interface ReturnFormProps {
  reservationId: string;
  isSubmitting: boolean;
  onSubmit: (payload: ReturnPayload) => void;
  onCancel: () => void;
}

export default function ReturnForm({
  reservationId,
  isSubmitting,
  onSubmit,
  onCancel
}: ReturnFormProps) {
  const { register, handleSubmit } = useForm<Omit<ReturnPayload, "reservation_id">>({
    defaultValues: { condition: "good", notes: "" }
  });

  return (
    <form
      className="space-y-4"
      onSubmit={handleSubmit((values) => onSubmit({ reservation_id: reservationId, ...values }))}
    >
      <label className="block text-sm font-semibold text-slate-700">
        Condition
        <select className="form-input mt-1" {...register("condition")}>
          <option value="good">Good</option>
          <option value="damaged">Damaged</option>
        </select>
      </label>
      <label className="block text-sm font-semibold text-slate-700">
        Notes
        <textarea className="form-input mt-1 min-h-24" {...register("notes")} />
      </label>
      <div className="flex gap-2">
        <button className="btn-primary" disabled={isSubmitting}>
          Submit return
        </button>
        <button className="btn-secondary" type="button" onClick={onCancel}>
          Cancel
        </button>
      </div>
    </form>
  );
}
