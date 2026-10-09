import {
  LogOut,
  Settings,
  User
} from "lucide-react";

import { useState } from "react";

function UserMenu({
  user,
  onLogout,
  onSettings
}) {
  const [open, setOpen] = useState(false);

  return (
    <div className="relative">

      <button
        onClick={() => setOpen(!open)}
        className="flex items-center gap-3 rounded-lg px-2 py-2 hover:bg-gray-800"
      >

        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-orange-500">
          <User
            size={17}
            className="text-white"
          />
        </div>

        <div className="hidden text-left sm:block">
          <p className="max-w-32 truncate text-sm font-medium text-gray-200">
            {user?.name || "User"}
          </p>

          <p className="max-w-32 truncate text-xs text-gray-500">
            {user?.email || ""}
          </p>
        </div>

      </button>

      {open && (
        <div className="absolute bottom-12 right-0 w-56 rounded-xl border border-gray-700 bg-gray-900 p-2 shadow-xl">

          <button
            onClick={() => {
              setOpen(false);
              onSettings();
            }}
            className="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm text-gray-300 hover:bg-gray-800"
          >
            <Settings size={17} />

            Settings
          </button>

          <button
            onClick={() => {
              setOpen(false);
              onLogout();
            }}
            className="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm text-red-400 hover:bg-gray-800"
          >
            <LogOut size={17} />

            Logout
          </button>

        </div>
      )}

    </div>
  );
}

export default UserMenu;