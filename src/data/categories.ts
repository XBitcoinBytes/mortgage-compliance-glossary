import type { CategoryId } from "../lib/types";

export interface CategoryMeta {
  id: CategoryId;
  label: string;
  esLabel: string;
  dek: string;
  esDek: string;
}

export const categories: CategoryMeta[] = [
  {
    id: "origination",
    label: "Origination",
    esLabel: "Originación",
    dek: "Application, Loan Estimate, rate lock, originator compensation, and the SAFE Act license.",
    esDek: "Solicitud, Estimación del préstamo, fijación de la tasa, compensación del originador y la licencia de la Ley SAFE.",
  },
  {
    id: "underwriting",
    label: "Underwriting",
    esLabel: "Suscripción",
    dek: "Income, assets, credit, collateral, ratios, AUS findings, and the condition stack.",
    esDek: "Ingresos, activos, crédito, garantía, relaciones, resultados del AUS y la lista de condiciones.",
  },
  {
    id: "compliance",
    label: "Compliance",
    esLabel: "Cumplimiento",
    dek: "Regulation Z, X, B, and C, ATR/QM, fair lending, UDAAP, flood, BSA/AML, and advertising.",
    esDek: "Reglamentos Z, X, B y C, capacidad de pago y QM, préstamos justos, UDAAP, inundación, BSA/AML y publicidad.",
  },
  {
    id: "closing",
    label: "Closing",
    esLabel: "Cierre",
    dek: "Closing Disclosure, tolerance buckets, cures, title, and the cash-to-close table.",
    esDek: "Divulgación del cierre, grupos de tolerancia, correcciones, título y la tabla de efectivo para el cierre.",
  },
  {
    id: "servicing",
    label: "Servicing",
    esLabel: "Administración",
    dek: "Escrow, transfers, error resolution, loss mitigation, foreclosure timing, and PMI cancellation.",
    esDek: "Depósito en garantía, transferencias, resolución de errores, mitigación de pérdidas, plazos de ejecución y cancelación del PMI.",
  },
  {
    id: "loan-programs",
    label: "Loan programs",
    esLabel: "Programas de préstamo",
    dek: "Conventional, FHA, VA, USDA, ARM, jumbo, HELOC, and reverse mortgages.",
    esDek: "Convencional, FHA, VA, USDA, ARM, jumbo, HELOC e hipotecas inversas.",
  },
  {
    id: "borrower-faqs",
    label: "Borrower questions",
    esLabel: "Preguntas de prestatarios",
    dek: "Plain questions borrowers ask, answered for the desk that has to explain them.",
    esDek: "Preguntas directas de los prestatarios, respondidas para quien tiene que explicarlas.",
  },
];

export const categoryMap = new Map(categories.map((category) => [category.id, category]));
