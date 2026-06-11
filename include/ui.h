#ifndef UI_H
#define UI_H

class UI {
public:
    UI();
    ~UI();
    
    void renderHUD();
    void renderStats(float fps, float hitRate);
    
private:
};

#endif // UI_H
