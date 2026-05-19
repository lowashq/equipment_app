import { useState } from "react";
import { useForm } from "react-hook-form";
import { Link } from "react-router-dom";

import { register as registerUser } from "../api/auth";
import { useAuth } from "../context/AuthContext";

interface RegisterForm {
  email: string;
  full_name: string;
  password: string;
}

export default function Register() {
  const { completeLogin } = useAuth();
  const { register, handleSubmit, formState } = useForm<RegisterForm>();
  const [error, setError] = useState("");

  const onSubmit = handleSubmit(async (values) => {
    setError("");
    try {
      const response = await registerUser(values);
      completeLogin(response);
    } catch (err: any) {
      setError(err.response?.data?.detail ?? "Could not register account.");
    }
  });

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-100 px-4">
      <div className="w-full max-w-md rounded-lg border border-line bg-white p-6 shadow-sm">
        <h1 className="text-2xl font-bold text-ink">Create account</h1>
        <p className="mt-1 text-sm text-slate-600">
          Registration is limited to university email domains.
        </p>

        <form className="mt-6 space-y-4" onSubmit={onSubmit}>
          <label className="block text-sm font-semibold text-slate-700">
            Full name
            <input className="form-input mt-1" {...register("full_name", { required: true })} />
          </label>
          <label className="block text-sm font-semibold text-slate-700">
            Email
            <input
              className="form-input mt-1"
              type="email"
              {...register("email", { required: true })}
            />
          </label>
          <label className="block text-sm font-semibold text-slate-700">
            Password
            <input
              className="form-input mt-1"
              type="password"
              {...register("password", { required: true, minLength: 6 })}
            />
          </label>
          {error && <p className="rounded bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>}
          <button className="btn-primary w-full" disabled={formState.isSubmitting}>
            Register
          </button>
        </form>

        <p className="mt-5 text-center text-sm text-slate-600">
          Already have an account?{" "}
          <Link className="font-semibold text-sky-700 hover:text-sky-900" to="/login">
            Login
          </Link>
        </p>
      </div>
    </div>
  );
}
