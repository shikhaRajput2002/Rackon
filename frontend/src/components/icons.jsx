const base = {
  width: 20,
  height: 20,
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 1.6,
  strokeLinecap: "round",
  strokeLinejoin: "round",
};

export const HomeIcon = (props) => (
  <svg {...base} {...props}>
    <path d="M3 10.5 12 3l9 7.5" />
    <path d="M5.5 9.5V20h13V9.5" />
    <path d="M9.5 20v-6h5v6" />
  </svg>
);

export const LedgerIcon = (props) => (
  <svg {...base} {...props}>
    <path d="M5 3.5h11l3 3V20.5H5z" />
    <path d="M8.5 9h7M8.5 13h7M8.5 17h4" />
  </svg>
);

export const ChartIcon = (props) => (
  <svg {...base} {...props}>
    <path d="M4 20V4" />
    <path d="M4 20h16" />
    <path d="M8 20v-6M12.5 20v-10M17 20v-4" />
  </svg>
);

/* The advisor's mark: a speech bubble with a spark inside it. */
export const AdvisorIcon = (props) => (
  <svg {...base} {...props}>
    <path d="M20.5 12.4c0 4.2-3.8 7.6-8.5 7.6a9.8 9.8 0 0 1-2.6-.35L4.2 21.2l1.3-3.7A7.2 7.2 0 0 1 3.5 12.4C3.5 8.2 7.3 4.8 12 4.8s8.5 3.4 8.5 7.6Z" />
    <path d="M12 8.6l1.05 2.3 2.35 1.05-2.35 1.05L12 15.3l-1.05-2.3-2.35-1.05 2.35-1.05Z" />
  </svg>
);

export const NoteIcon = (props) => (
  <svg {...base} {...props}>
    <path d="M6 3.5h12v17l-6-3.2-6 3.2z" />
  </svg>
);

export const UserIcon = (props) => (
  <svg {...base} {...props}>
    <circle cx="12" cy="8.5" r="3.75" />
    <path d="M4.75 20.5a7.25 7.25 0 0 1 14.5 0" />
  </svg>
);

export const PlusIcon = (props) => (
  <svg {...base} {...props}>
    <path d="M12 5.5v13M5.5 12h13" />
  </svg>
);

export const TrashIcon = (props) => (
  <svg {...base} {...props}>
    <path d="M4.5 6.5h15M9.5 6.5V4h5v2.5M6.5 6.5 7.5 20h9l1-13.5" />
  </svg>
);

export const PinIcon = (props) => (
  <svg {...base} {...props}>
    <path d="M9 3.5h6l-.8 6 3.3 3.2H6.5L9.8 9.5z" />
    <path d="M12 12.7V20.5" />
  </svg>
);

export const WalletIcon = (props) => (
  <svg {...base} {...props}>
    <path d="M3.5 7.5A2 2 0 0 1 5.5 5.5H17a1 1 0 0 1 1 1v1.5" />
    <path d="M3.5 7.5v10a1.5 1.5 0 0 0 1.5 1.5h14a1.5 1.5 0 0 0 1.5-1.5v-9A1.5 1.5 0 0 0 19 7H5.5" />
    <circle cx="16.5" cy="13" r="1.15" />
  </svg>
);

export const CompassIcon = (props) => (
  <svg {...base} {...props}>
    <circle cx="12" cy="12" r="8.5" />
    <path d="M15.2 8.8 13.6 13.6 8.8 15.2l1.6-4.8z" />
  </svg>
);

export const CalculatorIcon = (props) => (
  <svg {...base} {...props}>
    <rect x="5" y="3.5" width="14" height="17" rx="2" />
    <path d="M8.5 7.5h7" />
    <path d="M9 12h.01M12 12h.01M15 12h.01M9 16h.01M12 16h.01M15 16h.01" />
  </svg>
);

export const ScaleIcon = (props) => (
  <svg {...base} {...props}>
    <path d="M12 4.5v15" />
    <path d="M6.5 6.5h11" />
    <path d="M4 14.5 6.5 8l2.5 6.5a2.5 2.5 0 0 1-5 0Z" />
    <path d="M15 14.5 17.5 8l2.5 6.5a2.5 2.5 0 0 1-5 0Z" />
  </svg>
);

export const AlertIcon = (props) => (
  <svg {...base} {...props}>
    <circle cx="12" cy="12" r="8.5" />
    <path d="M12 7.75v5" />
    <path d="M12 16.1h.01" />
  </svg>
);

export const CheckIcon = (props) => (
  <svg {...base} {...props}>
    <path d="M5 12.5 10 17.5 19 7" />
  </svg>
);

export const ArrowLeftIcon = (props) => (
  <svg {...base} {...props}>
    <path d="M19 12H5.5" />
    <path d="M11 5.5 4.5 12l6.5 6.5" />
  </svg>
);

export const LockIcon = (props) => (
  <svg {...base} {...props}>
    <rect x="4.75" y="10.5" width="14.5" height="9.75" rx="2" />
    <path d="M8.25 10.5V7.75a3.75 3.75 0 0 1 7.5 0v2.75" />
  </svg>
);
