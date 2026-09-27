import traceback
import tkinter as tk
from tkinter import messagebox
from theme import apply_theme, BG


class App(tk.Tk):
    """
    Single-window controller.

    Every 'dashboard' used to be its own tk.Tk() instance, which is why the
    old version opened a separate OS window for every role. Here each
    dashboard is a Frame, and only ONE of them is mounted into `container`
    at a time -- so the whole app lives in one window/tab from login to
    logout.
    """

    def __init__(self):
        super().__init__()
        self.title("Food Donation & Redistribution System")
        self.geometry("1050x680")
        self.minsize(950, 600)
        apply_theme(self)

        self.container = tk.Frame(self, bg=BG)
        self.container.pack(fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self._frame = None
        self.go_to_login()

    def report_callback_exception(self, exc_type, exc_value, exc_tb):
        # Tkinter normally just prints callback errors to the terminal and
        # keeps going, which is how a broken page ends up silently blank.
        # Surface it as a popup too so it's never invisible.
        traceback.print_exception(exc_type, exc_value, exc_tb)
        messagebox.showerror("Unexpected Error", str(exc_value))

    def _mount(self, frame_class, **kwargs):
        # Build the new page BEFORE tearing down the old one: if
        # construction fails, the old page stays on screen (with an error
        # popup) instead of leaving a blank window.
        try:
            frame = frame_class(self.container, self, **kwargs)
        except Exception as e:
            traceback.print_exc()
            messagebox.showerror("Unexpected Error", str(e))
            return None

        if self._frame is not None:
            self._frame.destroy()
        frame.grid(row=0, column=0, sticky="nsew")
        self._frame = frame
        return frame

    def go_to_login(self, prefill_email=None):
        from pages.login_page import LoginPage
        self._mount(LoginPage, prefill_email=prefill_email)

    def go_to_register(self):
        from pages.register_page import RegisterPage
        self._mount(RegisterPage)

    def go_to_role(self, role, user_id, role_ref_id=None):
        if role == "ADMIN":
            from pages.admin_page import AdminPage
            self._mount(AdminPage, user_id=user_id)
        elif role == "PROVIDER":
            from pages.restaurant_page import RestaurantPage
            self._mount(RestaurantPage, user_id=user_id)
        elif role == "NGO":
            from pages.ngo_page import NgoPage
            self._mount(NgoPage, ngo_id=role_ref_id)
        elif role == "VOLUNTEER":
            from pages.volunteer_page import VolunteerPage
            self._mount(VolunteerPage, volunteer_id=role_ref_id)
        else:
            raise ValueError(f"Unknown role: {role}")

    def go_to_donation_manager(self, user_id):
        from pages.donation_manager_page import DonationManagerPage
        self._mount(DonationManagerPage, user_id=user_id)


if __name__ == "__main__":
    App().mainloop()
