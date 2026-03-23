# Frontend Ingress + Backend Connectivity Notes

## Summary
- Frontend initially used a dev server on port 3000 with `REACT_APP_API_URL` defaulting to `http://localhost:8000`, so browser requests could not route through Minikube's ingress and the service rewrite annotation caused static files to load HTML.
- Backend calls were being captured by the frontend ingress `path: /` rule, so the UI showed `404 /api/urls` despite the backend service serving correctly inside the cluster.

## Final Configuration
1. **Frontend service** listens on port 80 and runs the nginx-based production image built with `REACT_APP_API_URL=/api`. Build command: `REACT_APP_API_URL=/api npm run build` → image referenced in `frontend.yml`.
2. **Ingress split**:
   - `frontend-ingress.yml` routes `/` → `urlshortener-frontend-service:80` with no rewrite.
   - `bckend-ingress.yml` routes `/api(/|$)(.*)` → `urlshortener-backend-service:8000` and rewrites to `/api/$2` using regex annotations.
3. Ensure `urlshortener.local` resolves to the ingress controller IP (e.g., via `minikube tunnel`) so external requests actually reach the configured host.

## Troubleshooting Steps
- Run `kubectl get pods,svc,endpoints -n urlshortener` to verify services expose the expected ports and have endpoints.
- Look at controller logs (`kubectl logs -n ingress-nginx <controller-pod>`) whenever you face 502/503 to see which service/path is missing.
- Curl `http://urlshortener.local/api/urls` inside the cluster to confirm the backend ingresses rewrite correctly, then refresh the browser to validate the React bundle.

Keep this file with the repo as a quick reference for the ingress/frontend issue.
