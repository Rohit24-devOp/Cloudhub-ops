import React from "react";
import ReactDOM from "react-dom/client";
import { QueryClient, QueryClientProvider, useMutation, useQuery } from "@tanstack/react-query";
import axios from "axios";
import { Activity, Cloud, GitBranch, Lock, Network, Shield, Server, WalletCards } from "lucide-react";
import "./styles.css";

const api = axios.create({ baseURL: "/api" });
const queryClient = new QueryClient();

function setAuthHeader() {
  const token = localStorage.getItem("cloudops_access_token");
  if (token) api.defaults.headers.common.Authorization = `Bearer ${token}`;
  return token;
}

function Login() {
  const mutation = useMutation({
    mutationFn: async () => {
      const credentials = {
        email: "admin@codtechitsolutions.com",
        name: "CodTech Admin",
        password: "cloudops-secure-123"
      };
      const response = await api.post("/auth/register", credentials).catch(() => api.post("/auth/login", {
        email: credentials.email,
        password: credentials.password
      }));
      localStorage.setItem("cloudops_access_token", response.data.access_token);
      location.reload();
    }
  });
  return (
    <main className="login">
      <section>
        <p className="eyebrow">CodTech IT Solutions</p>
        <h1>CloudOps Hub</h1>
        <p>Provision, secure, monitor and deploy AWS infrastructure from one intelligent platform.</p>
        <button onClick={() => mutation.mutate()} disabled={mutation.isPending}>
          <Lock size={18} /> Start workspace
        </button>
      </section>
    </main>
  );
}

function Metric({ icon: Icon, label, value }: { icon: typeof Cloud; label: string; value: string | number }) {
  return <article className="metric"><Icon size={22} /><span>{label}</span><strong>{value}</strong></article>;
}

function Workspace() {
  const dashboard = useQuery({ queryKey: ["dashboard"], queryFn: async () => (await api.get("/dashboard")).data });
  const instances = useQuery({ queryKey: ["instances"], queryFn: async () => (await api.get("/instances")).data });
  const deployments = useQuery({ queryKey: ["deployments"], queryFn: async () => (await api.get("/deployments")).data });
  const createInstance = useMutation({
    mutationFn: () => api.post("/instances", { name: `api-${Date.now()}`, instance_type: "t3.medium", region: "ap-south-1" }),
    onSuccess: () => queryClient.invalidateQueries()
  });
  const deploy = useMutation({
    mutationFn: () => api.post("/deployments", { service: "cloudops-api", branch: "main" }),
    onSuccess: () => queryClient.invalidateQueries()
  });

  return (
    <div className="shell">
      <aside>
        <h2>CloudOps Hub</h2>
        <p>CodTech IT Solutions</p>
        <nav>
          <a><Activity size={18} /> Dashboard</a>
          <a><Shield size={18} /> IAM Audit</a>
          <a><Server size={18} /> EC2</a>
          <a><Network size={18} /> VPC Builder</a>
          <a><GitBranch size={18} /> CI/CD</a>
          <a><WalletCards size={18} /> Cost</a>
        </nav>
      </aside>
      <main>
        <header>
          <div>
            <p className="eyebrow">Production workspace</p>
            <h1>AWS operations command center</h1>
          </div>
          <button onClick={() => { localStorage.removeItem("cloudops_access_token"); location.reload(); }}>Sign out</button>
        </header>
        <section className="grid">
          <Metric icon={Shield} label="Security score" value={dashboard.data?.security_score ?? "-"} />
          <Metric icon={Server} label="Running EC2" value={dashboard.data?.running_instances ?? "-"} />
          <Metric icon={Activity} label="Open findings" value={dashboard.data?.open_findings ?? "-"} />
          <Metric icon={WalletCards} label="Monthly cost" value={`$${dashboard.data?.monthly_cost ?? 0}`} />
        </section>
        <section className="workbench">
          <article>
            <div className="row">
              <h2>EC2 Management</h2>
              <button onClick={() => createInstance.mutate()}>Launch instance</button>
            </div>
            {(instances.data ?? []).map((instance: any) => <div className="list-row" key={instance.id}><span>{instance.name}</span><b>{instance.status}</b><small>{instance.instance_type}</small></div>)}
          </article>
          <article>
            <div className="row">
              <h2>Deployment Center</h2>
              <button onClick={() => deploy.mutate()}>Deploy</button>
            </div>
            {(deployments.data ?? []).map((deployment: any) => <div className="list-row" key={deployment.id}><span>{deployment.service}</span><b>{deployment.status}</b><small>{deployment.branch}</small></div>)}
          </article>
        </section>
      </main>
    </div>
  );
}

function App() {
  const token = setAuthHeader();
  return (
    <QueryClientProvider client={queryClient}>
      {token ? <Workspace /> : <Login />}
    </QueryClientProvider>
  );
}

ReactDOM.createRoot(document.getElementById("root")!).render(<App />);
